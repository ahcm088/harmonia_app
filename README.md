# Editor de Cifras 🎶

Uma aplicação Kivy para editar cifras musicais com marcação de acordes, metadados harmônicos e comentários personalizados.

## ✨ Funcionalidades

- Inserção de acordes diretamente no texto usando a sintaxe `[Acorde]`
- Validação do formato do acorde ao inserir
- Visualização de acordes com e sem metadados coloridos (azul/vermelho)
- Adição de grau harmônico e comentários a cada acorde
- Lista lateral com todos os acordes e suas posições (linha/ordem)
- Edição completa do texto da cifra com atualização automática dos acordes
- Salvamento e carregamento de projetos `.harmonia.json`

## 🖼️ Interface

A interface é baseada no framework Kivy e organizada via arquivo KV (`ui.kv`), com os seguintes elementos:

- Campo de entrada para o texto da cifra
- Campos para adicionar acorde, grau e comentário
- Lista de acordes detectados com destaque visual
- Visualização formatada e colorida da cifra
- Painel de metadados
- Botões de salvar e carregar projeto

## 🛠️ Instalação

### Requisitos

- Python 3.7+
- Kivy 2.0+

### Instalação com `pip`

```bash
pip install kivy
```

## ▶️ Como executar

1. Clone este repositório ou baixe os arquivos `main.py` e `ui.kv`.
2. Execute o aplicativo:

```bash
python main.py
```

> Certifique-se de que `main.py` e `ui.kv` estão na mesma pasta.

## 💾 Formato de Projeto

Ao salvar um projeto, será criado um arquivo `.harmonia.json` contendo:

```json
{
  "title": "Título do projeto",
  "key": "Tom da música",
  "description": "Descrição",
  "lyrics_text": "Texto com acordes",
  "chord_metadata": {
    "pos_42": {
      "chord": "C#m",
      "degree": "iii",
      "comment": "Acorde de passagem"
    }
  }
}
```

## 📁 Estrutura do Projeto

```
.
├── main.py           # Código principal da aplicação
├── ui.kv             # Interface gráfica em Kivy
├── requirements.txt  # Dependências
└── README.md         # Documentação
```

## 🧪 Validação de acordes suportados

São aceitos acordes com as seguintes variações:

- Notas de A a G
- Sustenidos e bemóis (`#`, `b`)
- Tipos como: `m`, `maj`, `dim`, `aug`, `sus`, `add`, `7`, `9`, etc.
- Barra de baixo: `C/E`, `F#m/B`

## 📄 Licença

Distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais informações.