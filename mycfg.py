import json
import sys
import argparse
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


''' Assignment 2 functions '''
def get_path_lenths(cfg, entry):
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
    if not find_back_edges(cfg, entry):
        return True

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
        for u, succs in list(graph.items()):
            for v in list(succs):
                if v not in graph:
                    graph[v] = set()
                    preds[v] = preds.get(v, set())
                preds[v].add(u)

        # 3) Merge candidate
        rpo = reverse_postorder({k: list(vs) for k, vs in graph.items()}, entry)

        merged = False
        for a in rpo:
            if a not in preds:
                continue
            if len(preds[a]) == 1:
                p = next(iter(preds[a]))
                if a in graph[p]:
                    graph[p].remove(a)
                graph[p].update(graph.get(a, set()))
                graph.pop(a, None)
                for u in graph:
                    if a in graph[u]:
                        graph[u].remove(a)
                changed = True
                merged = True
                break

        if not merged and not changed:
            break

    return len(graph) == 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths", action="store_true")
    parser.add_argument("--rpo", action="store_true")
    parser.add_argument("--backs", action="store_true")
    parser.add_argument("--reducible", action="store_true")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    if args.all:
        args.paths = args.rpo = args.backs = args.reducible = True

    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        name2block = block_map(form_blocks(func["instrs"]))
        cfg = get_cfg(name2block)
        entry = next(iter(name2block))  # first block is the entry, Im not sure this is always true but that is my assumption

        # Always: print CFG
        print('digraph {} {{'.format(func['name']))
        for name in name2block:
            print( ' {};'.format(name))
        for name, succs in cfg.items():
            for succ in succs:
                print(' {} -> {};'.format(name,succ))
        print('}')

        # Optional extras
        if args.paths:
            print("paths:", get_path_lenths(cfg, entry))
        if args.rpo:
            print("rpo:", reverse_postorder(cfg, entry))
        if args.backs:
            print("backs:", find_back_edges(cfg, entry))
        if args.reducible:
            print("reducible:", is_reducible(cfg, entry))

