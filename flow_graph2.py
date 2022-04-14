# To generate overall file:
#   code2flow backend ai database cogitel_flask_app wsgi.py --output out.dot
#   dot -Tpdf out.dot -o flowchart.pdf

import codecs
import pydot
import ast
import astunparse
import os
import time

#  python3.6   conda   TensorFlow

class FunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.number = 0 # 节点编号
        self.s = '' # 简化ast串
        self.n2title = {} # 编号 -> 标题

    def print(self, v):
        self.s += str(v)

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def visit_FunctionDef(self, node):
        self.print('(')
        siz = len(node.body)
        for i in range(siz):
            fun_name = 'visit_' + type(node.body[i]).__name__
            if hasattr(self, fun_name):
                getattr(self, fun_name)(node.body[i])
            else:
                self.number += 1
                self.print(self.number)
                self.n2title[str(self.number)] = astunparse.unparse(node.body[i]).lstrip().rstrip()
            if i != siz - 1:
                self.print(',')
        self.print(')')

    # 忽略掉import等语句
    def visit_Import(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def visit_ImportFrom(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def visit_alias(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    # if语句
    def visit_If(self, node):
        # 条件
        self.print('i(')
        self.number += 1
        self.print(self.number)
        self.n2title[str(self.number)] = astunparse.unparse(node.test).lstrip().rstrip()
        # true分支
        self.print(',(')
        siz = len(node.body)
        for i in range(siz):
            fun_name = 'visit_' + type(node.body[i]).__name__
            if hasattr(self, fun_name):
                getattr(self, fun_name)(node.body[i])
            else:
                self.number += 1
                self.print(self.number)
                self.n2title[str(self.number)] = astunparse.unparse(node.body[i]).lstrip().rstrip()
            if i != siz - 1:
                self.print(',')
        # else分支
        self.print('),(')
        siz = len(node.orelse)
        for i in range(siz):
            fun_name = 'visit_' + type(node.orelse[i]).__name__
            if hasattr(self, fun_name):
                getattr(self, fun_name)(node.orelse[i])
            else:
                self.number += 1
                self.print(self.number)
                self.n2title[str(self.number)] = astunparse.unparse(node.orelse[i]).lstrip().rstrip()
            if i != siz - 1:
                self.print(',')
        self.print('))')

    # for 语句
    def visit_For(self, node):
        # 迭代器
        self.print('x(')
        self.number += 1
        self.print(self.number)
        a = astunparse.unparse(node.target).lstrip().rstrip()
        b = astunparse.unparse(node.iter).lstrip().rstrip()
        self.n2title[str(self.number)] = a + ' in ' + b
        # 循环体
        self.print(',(')
        siz = len(node.body)
        for i in range(siz):
            fun_name = 'visit_' + type(node.body[i]).__name__
            if hasattr(self, fun_name):
                getattr(self, fun_name)(node.body[i])
            else:
                self.number += 1
                self.print(self.number)
                self.n2title[str(self.number)] = astunparse.unparse(node.body[i]).lstrip().rstrip()
            if i != siz - 1:
                self.print(',')
        self.print('))')

    # while语句
    def visit_While(self, node):
        # 条件
        self.print('x(')
        self.number += 1
        self.print(self.number)
        self.n2title[str(self.number)] = astunparse.unparse(node.test).lstrip().rstrip()
        # 循环体
        self.print(',(')
        siz = len(node.body)
        for i in range(siz):
            fun_name = 'visit_' + type(node.body[i]).__name__
            if hasattr(self, fun_name):
                getattr(self, fun_name)(node.body[i])
            else:
                self.number += 1
                self.print(self.number)
                self.n2title[str(self.number)] = astunparse.unparse(node.body[i]).lstrip().rstrip()
            if i != siz - 1:
                self.print(',')
        self.print('))')

    def visit_Break(self, node):
        self.print('b')
        self.number += 1
        self.print(self.number)

    def visit_Continue(self, node):
        self.print('c')
        self.number += 1
        self.print(self.number)

    def visit_Return(self, node):
        self.print('r')
        self.number += 1
        self.print(self.number)
        if node.value == None:
            self.n2title['r' + str(self.number)] = 'return'
        else:
            self.n2title['r' + str(self.number)] = 'return ' + astunparse.unparse(node.value).lstrip().rstrip()

class CFG():
    def __init__(self):
        self.special_node = {}
        self.s = ''
        self.n2title = None
        self.idx = 0
        self.graph = None
    
    # 新建节点
    def new_node(self, title, node_shape='box', node_color='gray', text_fontsize=15):
        if title[0] == 'b':
            return pydot.Node(title, label='break', style='filled', shape=node_shape, fillcolor=node_color, fontname='Consolas', fontsize=text_fontsize)
        elif title[0] == 'c':
            return pydot.Node(title, label='continue', style='filled', shape=node_shape, fillcolor=node_color, fontname='Consolas', fontsize=text_fontsize)
        elif title[0] == 'r':
            return pydot.Node(title, label=self.n2title[title], style='filled', shape=node_shape, fillcolor=node_color, fontname='Consolas', fontsize=text_fontsize)
        elif title in self.n2title:
            return pydot.Node(title, label=self.n2title[title], style='filled', shape=node_shape, fillcolor=node_color, fontname='Consolas', fontsize=text_fontsize)
        else:
            return pydot.Node(title, label=title, style='filled', shape=node_shape, fillcolor=node_color, fontname='Consolas', fontsize=text_fontsize)

    # 新建边
    def new_edge(self, begin, end, title = ''):
        e = pydot.Edge(begin, end, label = title, color='black', arrowhead='open', fontname='Consolas', fontsize=15)
        if begin.get_shape() in ['ellipse', 'diamond']:
            if not begin.get_name() in self.special_node:
                self.special_node[begin.get_name()] = 1
                e.set_color('green')
                e.set_label('yes')
            else:
                e.set_color('red')
                e.set_label('no')
        return e

    # 匹配一个token
    def match(self):
        res = ''
        while self.s[self.idx] not in [',', ')']:
            res += self.s[self.idx]
            self.idx += 1
        return res

    # 检测是否不可达
    def check_unreachable(self, last_nodes):
        # 之前的节点为空显然不可达
        if len(last_nodes) == 0:
            return True
        ok = True
        # 之前全部不可达则当前也不可达
        for node in last_nodes:
            ok &= node.get_fillcolor() == 'red'
        return ok

    # 构建分支语句CFG
    def build_If(self, last_nodes, continue_node, break_nodes, return_nodes):
        self.idx += 1
        if not self.check_unreachable(last_nodes):
            node0 = self.new_node(self.match(), node_shape='diamond', node_color='orange')
        else: # 不可达结点置为红色
            node0 = self.new_node(self.match(), node_shape='diamond', node_color='red')
        self.graph.add_node(node0)
        for node in last_nodes:
            self.graph.add_edge(self.new_edge(node, node0))
        self.idx += 1
        nodes1 = self.build_CFG([node0], continue_node, break_nodes, return_nodes)
        self.idx += 1
        nodes2 = self.build_CFG([node0], continue_node, break_nodes, return_nodes)
        self.idx += 1
        nodes1.extend(nodes2)
        return nodes1

    # 构建循环语句CFG
    def build_For(self, last_nodes, return_nodes):
        self.idx += 1
        if not self.check_unreachable(last_nodes):
            node0 = self.new_node(self.match(), node_shape='ellipse', node_color='deeppink')
        else:
            node0 = self.new_node(self.match(), node_shape='ellipse', node_color='red')
        self.graph.add_node(node0)
        for node in last_nodes:
            self.graph.add_edge(self.new_edge(node, node0))
        self.idx += 1
        break_nodes = [] # 收集break节点
        nodes1 = self.build_CFG([node0], node0, break_nodes, return_nodes)
        for node in nodes1:
            self.graph.add_edge(self.new_edge(node, node0))
        self.idx += 1
        break_nodes.append(node0)
        return break_nodes

    # 构建CFG
    def build_CFG(self, last_nodes, continue_node, break_nodes, return_nodes):
        self.idx += 1
        while self.s[self.idx] != ')':
            if self.s[self.idx] == ',':
                self.idx += 1
                continue
            if self.s[self.idx] == 'i': # 分支语句
                self.idx += 1
                last_nodes = self.build_If(last_nodes, continue_node, break_nodes, return_nodes)
            elif self.s[self.idx] == 'x': # 循环语句
                self.idx += 1
                last_nodes = self.build_For(last_nodes, return_nodes)
            elif self.s[self.idx] == 'b': # break语句
                if not self.check_unreachable(last_nodes):
                    node0 = self.new_node(self.match())
                else:
                    node0 = self.new_node(self.match(), node_color='red')
                self.graph.add_node(node0)
                break_nodes.append(node0)
                for node in last_nodes:
                    self.graph.add_edge(self.new_edge(node, node0))
                last_nodes.clear()
            elif self.s[self.idx] == 'c': # continue语句
                if not self.check_unreachable(last_nodes):
                    node0 = self.new_node(self.match())
                else:
                    node0 = self.new_node(self.match(), node_color='red')
                self.graph.add_node(node0)
                for node in last_nodes:
                    self.graph.add_edge(self.new_edge(node, node0))
                self.graph.add_edge(self.new_edge(node0, continue_node))
                last_nodes.clear()
            elif self.s[self.idx] == 'r': # return语句
                if not self.check_unreachable(last_nodes):
                    node0 = self.new_node(self.match())
                else:
                    node0 = self.new_node(self.match(), node_color='red')
                self.graph.add_node(node0)
                return_nodes.append(node0)
                for node in last_nodes:
                    self.graph.add_edge(self.new_edge(node, node0))
                last_nodes.clear()
            else: # 一般语句
                if not self.check_unreachable(last_nodes):
                    node0 = self.new_node(self.match())
                else:
                    node0 = self.new_node(self.match(), node_color='red')
                self.graph.add_node(node0)
                for node in last_nodes:
                    self.graph.add_edge(self.new_edge(node, node0))
                last_nodes = [node0]
        self.idx += 1
        return last_nodes

    # 从ast构建CFG
    def build_CFG_from_ast(self, tree):
        visitor = FunctionVisitor()
        visitor.visit(tree)
        self.special_node.clear()
        self.s = visitor.s
        self.n2title = visitor.n2title
        self.idx = 0
        self.graph = pydot.Dot(graph_type = 'digraph')
        node_entry = self.new_node('Entry', node_shape='Msquare', node_color='green')
        self.graph.add_node(node_entry)
        return_nodes = [] # 收集return节点
        last_nodes = self.build_CFG([node_entry], None, [], return_nodes)
        last_nodes.extend(return_nodes)
        node_end = self.new_node('End', node_shape='Msquare', node_color='brown')
        self.graph.add_node(node_end)
        for node in last_nodes:
            self.graph.add_edge(self.new_edge(node, node_end))
        return self.graph

class CFGGenerator(ast.NodeVisitor):
    def __init__(self, cfg, folder):
        self.cfg = cfg # CFG对象
        self.folder = folder # 保存CFG的文件夹
        self.prefix = '' # 类名前缀

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def visit_ClassDef(self, node):
        self.prefix = node.name
        ast.NodeVisitor.generic_visit(self, node)
    
    def visit_FunctionDef(self, node):
        graph = self.cfg.build_CFG_from_ast(node)
        if len(self.prefix) == 0:
            path = node.name + '.pdf'
        else:
            path = self.prefix + '.' + node.name + '.pdf'
        path = os.path.join(self.folder, path)
        graph.write_pdf(path)
        print('generate ' + path)

if __name__ == '__main__':
    base_folder = "CFG"
    file_folder = "backend"
    filename = "ext"

    try:
        fp = os.path.join(file_folder, filename) + ".py"
        folder = base_folder + filename

        if not os.path.exists(folder):
            os.makedirs(folder)

        file = codecs.open(fp, 'r', 'utf-8')
        code = file.read()
        file.close()
        st = time.time()

        tree = ast.parse(code)

        cfg = CFG()
        generator = CFGGenerator(cfg, folder)
        generator.visit(tree)
        ed = time.time()
        print("time: %.3f s" % (ed - st))
    except Exception as e:
        print('Error:', e)