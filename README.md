# 🎶 Harmonauta

**Harmonauta** é um editor de cifras musicais inteligente construído com Python e Kivy. Ele permite inserir acordes dentro da letra da música, associar comentários e graus harmônicos a cada acorde, salvar e carregar projetos, e até mesmo buscar letras automaticamente do site [letras.com](https://www.letras.com).

---

## 🚀 Funcionalidades

- 📌 Inserção de acordes com validação
- 📝 Anotações personalizadas de grau harmônico e comentários
- 🎯 Visualização em tempo real com realce de acordes
- 💾 Salvamento e carregamento de projetos `.harmonia.json`
- 🌐 Busca automática de letras no letras.com
- 🎨 Interface gráfica intuitiva com splash screen personalizada
- 🧼 Função de reset para começar um novo projeto rapidamente

---

## 🖼️ Imagens e Layout

- O projeto usa um arquivo `.kv` para definir a interface gráfica.
- A splash screen exibe um logo localizado em `assets/harmonauta_splash.png`.
- O ícone do aplicativo é `assets/harmonauta_logo.png`.

---

## 📁 Estrutura de Pastas

```
harmonauta/
│
├── main.py               # Lógica principal do aplicativo
├── ui.kv                 # Interface visual com Kivy Language
├── assets/
│   ├── harmonauta_splash.png
│   └── harmonauta_logo.png
└── README.md
```

---

## ▶️ Executando o Projeto

Certifique-se de ter o Python 3.7+ instalado. Em seguida, instale as dependências e execute o app:

```bash
pip install kivy requests beautifulsoup4
python main.py
```

---

## 📱 Requisitos

- Python 3.7 ou superior
- [Kivy](https://kivy.org/#download) >= 2.1
- `requests`
- `beautifulsoup4`

---

## 📦 Gerar APK para Android

Você pode empacotar o app para Android usando o [Buildozer](https://github.com/kivy/buildozer):

```bash
pip install buildozer
buildozer init
# Edite o buildozer.spec conforme necessário
buildozer -v android debug
```

Ou use um serviço de build online como o [Kivy Launcher](https://kivy.org/doc/stable/guide/packaging-android.html) para testar rapidamente.

---

## 🧠 Créditos

Desenvolvido por Alexandre Marques.  
Inspirado na ideia de facilitar a análise e anotação harmônica de cifras musicais para músicos, estudantes e pesquisadores.

---

## 📃 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.
