# Harmonia App

Editor de cifras e análise harmônica para músicos, construído em Python com Kivy.

## Funcionalidades

- Inserção de acordes diretamente na letra da música usando formato `[Am]`
- Metadados para cada ocorrência de acorde, como grau harmônico e comentários
- Visualização da cifra com acordes coloridos (vermelho = sem metadados; azul = com metadados)
- Edição e atualização dinâmica dos metadados por ocorrência do acorde
- Interface amigável para computador e potencial para dispositivos móveis

## Como usar

1. Digite ou cole a letra da música no campo à esquerda.
2. Posicione o cursor na palavra onde deseja inserir o acorde.
3. Digite o acorde no campo "Acorde" e clique em "Inserir acorde".
4. Se desejar, preencha os campos "Grau harmônico" e "Comentário sobre o acorde" antes de inserir, para que já sejam vinculados.
5. Clique em uma ocorrência de acorde na lista à direita para editar seus metadados.
6. Use os botões para atualizar ou limpar os campos de metadados.

## Requisitos

- Python 3.8 ou superior
- Kivy 2.3.1

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\activate     # Windows

pip install kivy
