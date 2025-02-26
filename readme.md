# Snake Deep Learning

Ce projet permet d'entraîner une IA pour jouer au jeu Snake.

## Exécution

### **Entraîner l'IA**
```bash
python train.py --mode train --episodes 3000 --qtable snake_q_table.json --tick 1500
```

### **Jouer avec l'IA**
```bash
python train.py --mode play --games 10 --qtable snake_q_table.json --tick 10
```

## Arguments disponibles

| Argument | Valeurs possibles | Description |
|----------|------------------|-------------|
| `--mode` | `train`, `play` | Mode d'exécution : entraînement ou jeu |
| `--episodes` | `1` à `∞` | Nombre d'épisodes pour l'entraînement |
| `--games` | `1` à `∞` | Nombre de parties jouées par l'IA |
| `--qtable` | Nom de fichier | Fichier pour sauvegarder ou charger la Q-table |
| `--tick` | `1` à `∞` | Vitesse du jeu (plus élevé = plus rapide) |

Exemple :
```bash
python train.py --mode play --games 5 --qtable my_qtable.json --tick 10
```

