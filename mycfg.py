
import json
import sys
from collections import OrderedDict, deque, defaultdict


TERMINATORS = ('jmp','br','ret')

def form_blocks(body):
    cur_block = []

    for instr in body: 
        if 'op' in instr:   # An actually instruction
            cur_block.append(instr)

            # Check for terminator
            if instr['op'] in TERMINATORS:
                yield cur_block
                cur_block = []

        else:               # label
            if cur_block:
                yield cur_block          
            cur_block = [instr]
    if cur_block:
        yield cur_block


def block_map(blocks):
    out = OrderedDict()

    for block in blocks:
        if 'label' in block[0]:
            name = block[0]['label']
            block = block[1:]
        else:
            name = 'b{}'.format(len(out))
        

        out[name] = block

    return out

 
    
def get_cfg(name2block):
    """Given a name->block mapping, produce {block_name: [successor_block_names]}."""
    out = {}
    keys = list(name2block.keys())  # preserves the existing order
    for i, (name, block) in enumerate(name2block.items()):
        last = block[-1]
        if last['op'] in ('jmp', 'br'):
            succ = last.get('labels', [])
        elif last['op'] == 'ret':
            succ = []
        else:
            if i == len(keys) - 1:
                succ = []
            else:
                succ = [keys[i + 1]]
        out[name] = succ
    return out


''' Assingmet 2 functions '''
def get_path_lenths(cfg, entry):
    '''
    Compute the shortest path length from the entry node to each reachable node in the CFG
    using BFS. Unreachable nodes are ommited.
    '''

    dist = {entry: 0 }
    q = deque([entry])

    while q:
        u = q.popleft()
        for v in cfg.get(u,[]):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist

def reverse_postorder(cfg, entry):
    '''
    Compute reverse postorder for cfg onlu nodes reachable from entry are used.
    '''
    visited = set()
    post = []

    def dfs(u):
        if u in visited:
            return
        visited.add(u)
        for v in cfg.get(u,[]):
            dfs(v)
        post.append(u)

    dfs(entry)
    post.reverse()
    return post

def find_back_edges(cfg, entry):
    """
    Find back edges in the CFG using DFS.
    """
    visited = set()
    stack = set()
    back_edges = []

    def dfs(u):
        visited.add(u)
        stack.add(u)
        for v in cfg.get(u, []):
            if v not in visited:
                dfs(v)
            elif v in stack:
                # v is still active in the DFS stack = back edge
                back_edges.append((u, v))
        stack.remove(u)

    dfs(entry)
    return back_edges



def mycfg():
    prog = json.load(sys.stdin)
    for func in prog['functions']:
        name2block = block_map(form_blocks(func['instrs']))
        cfg = get_cfg(name2block)

        print('digraph {} {{'.format(func['name']))

        for name in name2block:
            print( ' {};'.format(name))
        for name, succs in cfg.items():
            for succ in succs:
                print(' {} -> {};'.format(name,succ))
        print('}')

def is_reducible(cfg, entry):
    """
    Reduction test
      - If there are no back edges => reducible 
      - Else, repeat until no change:
          * remove self-edges
          * pick a node A with exactly one predecessor P and merge A into P
      - Reducible if one node remains.
    """
    # acyclic graphs are reducible
    if not find_back_edges(cfg, entry):
        return True

    # Mutable copy (use sets for simple edge edits)
    graph = {u: set(succs) for u, succs in cfg.items()}

    while True:
        changed = False

        # 1) Remove self-edges
        for u in list(graph.keys()):
            if u in graph[u]:
                graph[u].remove(u)
                changed = True

        # 2) Rebuild predecessors
        preds = {u: set() for u in graph}
        for u, succs in graph.items():
            for v in succs:
                # Ensure 'v' exists even if it wasn’t an explicit key
                if v not in graph:
                    graph[v] = set()
                    preds[v] = preds.get(v, set())
                preds[v].add(u)

        # 3) Find a merge candidate using reverse postorder for determinism
        rpo = reverse_postorder({k: list(vs) for k, vs in graph.items()}, entry)

        merged = False
        for a in rpo:
            if a not in preds:     # might have been removed mid-loop
                continue
            if len(preds[a]) == 1:
                p = next(iter(preds[a]))
                # splice: p = (p \ {a}) ∪ succ(a)
                if a in graph[p]:
                    graph[p].remove(a)
                graph[p].update(graph.get(a, set()))

                # remove 'a' from the graph and from all succ lists
                graph.pop(a, None)
                for u in graph:
                    if a in graph[u]:
                        graph[u].remove(a)

                changed = True
                merged = True
                break  # re-run the outer loop after a single merge

        if not merged and not changed:
            break

    return len(graph) == 1



'''




def find_back_edges(cfg, entry):

"""

Find back edges in a CFG using DFS.


Parameters:

cfg(dict): mapping {node: [successors]}

entry(str): starting node


Returns: list of edges (u,v) where u->v is a back edge

"""

def is_reducible(cfg, entry):

"""

Determine whether a CFG is reducible.


Parameters:

cfg(dict): mapping {node: [successors]}

entry(str): starting node


Returns: True if the CFG is reducible or False if the CFG is irreducible


'''
        

if __name__ == "__main__":
    mycfg()