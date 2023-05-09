import yaml
import os, sys

def build_config(max_round=None, initial_stack=None, small_blind=None, ante=None, blind_structure=None):
    config = {
            "max_round": max_round,
            "initial_stack": initial_stack,
            "small_blind": small_blind,
            "ante": ante,
            "blind_structure": blind_structure,
            "ai_players": [
                { "name": "FIXME:your-ai-name", "path": "FIXME:your-setup-script-path" },
            ]
            }
    print(yaml.dump(config, default_flow_style=False))

if __name__ == '__main__':
    # redirect the output into a file called poker_conf.yaml
    orig_stdout = sys.stdout
    f = open('poker_conf.yaml', 'w')
    sys.stdout = f

    build_config(max_round=10, initial_stack=100, small_blind=10, ante=0) 

    sys.stdout = orig_stdout
    f.close()
