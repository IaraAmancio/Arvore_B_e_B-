
#BTree - Implementação de B-tree em Python para fins didáticos.
# Inclui algoritmos para adicionar, pesquisar e excluir valores de
# a árvore B.
# A pesquisa dentro dos nós é feita usando a pesquisa binária (usando
# o módulo da bissetriz).
#

import bisect
from random import randint
""" Um nó de árvore B é uma classe concreta. Contém uma lista ordenada
    de valores e - no caso de nós internos - a lista dos
    filhos _BTreeNode correspondentes que são separados por
    aqueles valores. O membro pai faz referência ao nó pai
    ou Nenhum no caso do nó raiz.
"""


class _BTreeNode(object):
    def __init__(self, values=None, children=None):
        self.parent = None
        self.values = values or []
        self.children = children
        # atualizar o nó pai em filhos,
        # apenas no caso de ter mudado
        if self.children:
            for i in self.children:
                i.parent = self

    def __str__(self):
        return '%r' % (
            self.values
            #len(self.children) if self.children else 0
        )

    def pretty_print(self, tab=''):

        print('%s%s' % (tab, self))
        if self.children:
            for i in self.children:
                i.pretty_print(tab+ '  ')

    """ Verifique (recursivamente) a integridade da árvore de acordo com as regras da árvore B.
        Isso é usado para verificar a exatidão dos algoritmos.
    """

    def check_valid(self, tree):
        innerNode = self.children is not None
        rootNode = self.parent is None

        assert (self.values is not None)

        # um nó interno, exceto a raiz, tem pelo menos min_values
        if not rootNode and innerNode:

            assert (tree.min_values <= len(self.values))

        # um nó não pode ter mais de max_values
        assert (len(self.values) <= tree.max_values)

        # A raiz tem pelo menos dois filhos se não for um nó folha.
        if rootNode and innerNode:
            assert (len(self.children) >= 2)

        # Um nó não folha com k filhos contém k-1 chaves.
        if innerNode:
            assert ((len(self.values) + 1) == len(self.children))

        # check that values are sorted
        prev = None
        for i in self.values:
            if prev is not None:
                assert (i > prev)
            prev = i

        if self.children:
            for i in self.children:
                assert (i.parent is self)
                i.check_valid(tree)

    """
    Procure um valor começando com este nó.

    Se o valor não existir na árvore, desça na árvore e
    retornar o nó folha e a posição de inserção nesse nó onde
    o valor deve ser colocado. ou seja, a tupla: (Falso, nó, pos)

    Se val existir na árvore, retorne a tupple: (True, node, pos),
    onde node é o nodo que contém o valor e pos é o
    posição do valor dentro desse nó.
    """

    def search(self, val):
        i = bisect.bisect_left(self.values, val)
        if (i != len(self.values) and not val < self.values[i]):
            # a value was found
            assert (self.values[i] == val)
            return (True, self, i)

        if self.children is not None:
            assert (len(self.children) >= i and self.children[i])
            # recursively search down the appropriate child node
            return self.children[i].search(val)
        else:
            return (False, self, i)

    """ Split a B-tree node in two.

        If val and slot are given then also ins ert val into the
        resulting nodes. If additionally childNodes is given 
        then _split_node is recursively called from add and
        childNodes represent the nodes separated by the value val
        in this node's parent.
    """

    def _split_node(self, tree, val=None, slot=None, childNodes=None):
        assert (val is None or (slot is not None))
        midList = [] if val is None else [val]
        if slot is None:
            slot = 0

        # obtenha a mediana de self.values e val
        splitValues = self.values[0:slot] + midList + self.values[slot:]
        if (tree.order % 2 == 0):
            medianIdx = len(splitValues) // 2 - 1
        else:
            medianIdx = len(splitValues) // 2
        lv = splitValues[0:medianIdx]
        medianVal = splitValues[medianIdx]
        rv = splitValues[medianIdx + 1:]

        innerNode = self.children is not None

        if innerNode:
            if childNodes is not None:
                splitChildren = (self.children[0:slot] +
                                 list(childNodes) +
                                 self.children[slot + 1:])
            else:
                splitChildren = self.children
            lc = splitChildren[0:len(lv) + 1]
            rc = splitChildren[len(lv) + 1:]
        else:
            lc = None
            rc = None

        leftNode = _BTreeNode(lv, lc)
        rightNode = _BTreeNode(rv, rc)

        if self.parent:
            self.parent.add(tree,
                            medianVal,
                            None,
                            (leftNode, rightNode))
        else:
            # create new root and increment the tree depth
            newRoot = _BTreeNode([medianVal], [leftNode, rightNode])
            leftNode.parent = newRoot
            rightNode.parent = newRoot
            tree.root = newRoot
            tree.height += 1
            tree.size += 1

    """
    Add a new value to the B-tree 'tree'.

    The value must not already exist.
    """

    def add(self, tree, val, slot=None, childNodes=None):
        # todas as inserções devem começar em um nó folha,
        # a menos que chamemos add recursivamente no pai
        # como resultado da divisão do nó
        # quando estamos adicionando o valor mediano ao pai
        assert (self.children is None or childNodes)

        # se este for um nó interno se não for uma folha ou a raiz
        # então self.children não é None, então também
        # esta função deve ter sido chamada recursivamente
        # with childNodes not None, val not None e
        # len(childNodes) == 2
        innerNode = self.children is not None
        if innerNode:
            assert (childNodes and len(childNodes) == 2)
        else:
            assert (childNodes is None)

        # se ainda não encontrado, encontre a posição de inserção entre
         # os valores do nó atual
        if slot is None:
            slot = bisect.bisect_left(self.values, val)

        # podemos fazer a inserção nos valores do nó atual?
        if len(self.values) < tree.max_values:
            self.values.insert(slot, val)
            tree.size += 1
            if childNodes:
                # atualize a referência pai nos nós que estamos prestes a adicionar
                for i in childNodes:
                    i.parent = self
                self.children[slot:slot + 1] = childNodes
            # Foram realizadas
            return True

        # parece que o nó atual está cheio, temos que dividi-lo
        self._split_node(tree, val, slot, childNodes)
        return True

    def min_value(self, slot=0):
        if self.children:
            return self.children[slot].min_value()
        return self.values[0], self, 0

    def max_value(self, slot=None):
        if slot is None:
            slot = len(self.values) - 1
        if self.children:
            return self.children[slot + 1].max_value()
        return self.values[-1], self, len(self.values) - 1

    """
    Delete a value from the B-tree.
    The value must exist.
    """

    def delete(self, tree, val, slot=None):

        innerNode = self.children is not None
        if slot is None:
            assert (slot is not None)
            slot = bisect.bisect_left(self.values, val)

        assert (slot != len(self.values) and self.values[slot] == val)

        if not innerNode:
            # perform deletion from a leaf
            del self.values[slot]
            tree.size -= 1
            if len(self.values) < tree.min_values:
                # underflow happened in the leaf node
                # rebalance tree starting with this node
                self._rebalance(tree)
        else:
            # find the minimum value in the right subtree
            # and use it as the separator value to replace val
            newSep, node, idx = self.min_value(slot + 1)
            self.values[slot] = newSep
            del node.values[idx]
            tree.size -= 1
            if len(node.values) < tree.min_values:
                node._rebalance(tree)

    """ Rebalance a B-tree starting with the current node.
    """

    def _rebalance(self, tree):
        lsibling, rsibling, idx = self.get_siblings()

        # only the root doesn't have siblings
        assert (rsibling or lsibling or self.parent is None)

        if self.parent is None:
            # this is a no-op for the root node
            return

        innerNode = self.children is not None
        if innerNode:
            assert (rsibling is None or rsibling.children is not None)
            assert (lsibling is None or lsibling.children is not None)
        else:
            assert (rsibling is None or rsibling.children is None)
            assert (lsibling is None or lsibling.children is None)

        if not innerNode:
            if rsibling and len(rsibling.values) > tree.min_values:
                sepIdx = idx
                sepVal = self.parent.values[sepIdx]
                # borrow node from rsibling to perform a left rotate
                self.parent.values[sepIdx] = rsibling.values[0]
                del rsibling.values[0]
                self.values.append(sepVal)
                return
            elif lsibling and len(lsibling.values) > tree.min_values:
                sepIdx = idx - 1
                sepVal = self.parent.values[sepIdx]
                # borrow node from lsibling to perform a right rotate
                self.parent.values[sepIdx] = lsibling.values[-1]
                del lsibling.values[-1]
                self.values.insert(0, sepVal)
                return

        # we have to merge 2 nodes
        if lsibling is not None:
            sepIdx = idx - 1
            ln = lsibling
            rn = self
        elif rsibling is not None:
            sepIdx = idx
            ln = self
            rn = rsibling
        else:
            assert (False)

        sepVal = self.parent.values[sepIdx]

        ln.values.append(sepVal)
        ln.values.extend(rn.values)
        del rn.values[:]
        del self.parent.values[sepIdx]
        assert (self.parent.children[sepIdx + 1] is rn)
        del self.parent.children[sepIdx + 1]
        if rn.children:
            ln.children.extend(rn.children)
            for i in rn.children:
                i.parent = ln

        if len(ln.values) > tree.max_values:
            # we have to split the newly formed node
            # this situation can aris only when merging inner nodes
            assert (innerNode)
            ln._split_node(tree)

        if len(self.parent.values) < tree.min_values:
            # rebalance the parent
            self.parent._rebalance(tree)

        if self.parent.parent is None and not self.parent.values:
            tree.root = ln
            tree.root.parent = None

    """ Get the adjacent siblings of this node.

    Return the tupple:
    (left sibiling node, right sibling node, separator index).
    If a sibling does not exist, None is returned instead. The 
    separator index represents the index of this node in its 
    parent's children list.
    """

    def get_siblings(self):
        if not self.parent:
            # the root doesn't have siblings
            return (None, None, 0)

        assert (self.parent.children)

        lsibling = None
        rsibling = None
        idx = 0

        for i, j in enumerate(self.parent.children):
            if j is self:
                if i != 0:
                    lsibling = self.parent.children[i - 1]
                if (i + 1) < len(self.parent.children):
                    rsibling = self.parent.children[i + 1]
                idx = i
                break

        return (lsibling, rsibling, idx)


""" B-tree implementation operating on _BTreeNode-s.

    It implements the interface for constructing, editing and 
    searching in B-trees.
"""


class BTree(object):
    """ Create a B-tree of a given order. The order is
        interpreted as the maximum number of children per node,
        which is the maximum number of keys per node plus one.
        See: Knuth, Donald, Sorting and Searching, The Art of
        Computer Programming, Volume 3 p. 483.
    """

    def __init__(self, order):
        if order <= 2:
            raise ValueError("B-tree order must be at least 3")
        self.root = _BTreeNode()
        self.order = order
        self.max_values = order - 1
        self.min_values = self.max_values // 2
        self.height = 1
        self.size = 0

    def __str__(self):
        return 'height: %d items: %d m: %d root: %x' % (
            self.height, self.size,
            self.max_values + 1,
            id(self.root))

    def add(self, val):
        # encontre o nó folha onde o valor deve ser adicionado
        found, node, slot = self.root.search(val)
        """if found:
            # o valor já existe, não pode adicioná-lo duas vezes
            return False"""
        return node.add(self, val, slot, None)

    def delete(self, val):
        # find the value and its
        found, node, slot = self.root.search(val)
        if not found:
            # the value doesn't exist, can't delete it
            return False
        return node.delete(self, val, slot)

    def search(self, val):
        return self.root.search(val)[0]

    def min(self):
        return self.root.min_value()[0]

    def max(self):
        return self.root.max_value()[0]


if __name__ == '__main__':

    tree = BTree(4) # grau da árvore
    n = 20 # número de valores
    for i in range(1, n):
        aleatorio = randint(0,50)
        tree.add(aleatorio)


    print("B-tree")
    tree.root.pretty_print()
    print("-------")
   # tree.root.check_valid(tree)
"""
    for i in range(1, 4):
        tree.delete(i)
        tree.root.check_valid(tree)"""