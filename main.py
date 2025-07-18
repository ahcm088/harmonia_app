import json
import re
from pathlib import Path
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.properties import (DictProperty, StringProperty, 
                           ListProperty, ObjectProperty)
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from kivy.utils import platform
from kivy.graphics import Color, Rectangle  # Para o fundo colorido
from kivy.uix.progressbar import ProgressBar  # Para a barra de progresso
from kivy.animation import Animation  # Para animar a barra de progresso
from kivy.resources import resource_add_path
import os

resource_add_path(os.path.join(os.path.dirname(__file__), 'assets'))

class SplashScreen(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Configura o fundo
        with self.canvas.before:
            Color(1, 1, 1, 1)  # Cor do seu app
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        
        # Container principal
        layout = BoxLayout(orientation='vertical', padding=50)
        
        # Imagem central
        self.logo = Image(
            source= "harmonauta_splash.png",
            size_hint=(None, None),
            size=(min(Window.width, Window.height) * 0.7, 
                min(Window.width, Window.height) * 0.7),
            pos_hint={'center_x': 0.5},
            allow_stretch=False,  # Substitui o keep_ratio
            keep_data=False       # Novo parâmetro recomendado
        )
        
        # Label de status
        self.label = Label(
            text="Inicializando...",
            font_size='18sp',
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=40
        )
        
        # Barra de progresso
        self.progress = ProgressBar(
            max=100,
            size_hint=(1, None),
            height=20,
            value=0
        )
        
        layout.add_widget(self.logo)
        layout.add_widget(self.label)
        layout.add_widget(self.progress)
        self.add_widget(layout)
        
        # Animação da barra de progresso
        self.animate_progress()
    
    def animate_progress(self):
        anim = Animation(value=100, duration=2.5)
        anim.start(self.progress)

class HarmonyScreen(BoxLayout):
    selected_occurrence = StringProperty("")
    chord_metadata = DictProperty({})
    project_title = StringProperty("Sem título")
    project_key = StringProperty("")
    project_description = StringProperty("")
    chord_positions = ListProperty([])
    chord_counter_map = DictProperty({})
    selected_button = ObjectProperty(None, allownone=True)
    last_text = StringProperty("")
    last_used_dir = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(chord_positions=self.update_chord_buttons)
        self.setup_default_dirs()

    def setup_default_dirs(self):
        """Configura os diretórios padrão baseado no sistema operacional"""
        if platform == "android":
            try:
                from android.storage import primary_external_storage_path
                self.default_dir = str(Path(primary_external_storage_path()) / "HarmonyProjects")
                Path(self.default_dir).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.default_dir = str(Path.home())
        else:
            self.default_dir = str(Path.home() / "Documents" / "HarmonyProjects")
            Path(self.default_dir).mkdir(parents=True, exist_ok=True)
        
        # Tenta usar o último diretório usado ou cria o padrão
        if not self.last_used_dir:
            self.last_used_dir = self.default_dir
            Path(self.default_dir).mkdir(parents=True, exist_ok=True)

    def on_text_change(self, instance, value):
        """Chamado quando o texto da cifra é alterado"""
        if hasattr(self, 'last_text'):
            old_lines = self.last_text.split('\n')
            new_lines = value.split('\n')
            
            if len(new_lines) != len(old_lines):
                self.parse_chords()
                self.last_text = value
                return
            
            for i, old_line in enumerate(old_lines):
                if i >= len(new_lines):
                    self.parse_chords()
                    self.last_text = value
                    return
        
        self.last_text = value
        self.parse_chords()

    def insert_chord_tag(self):
        cursor_index = self.ids.lyrics_input.cursor_index()
        text = self.ids.lyrics_input.text
        chord = self.ids.chord_input.text.strip()
        degree = self.ids.degree_input.text.strip()
        comment = self.ids.comment_input.text.strip()

        if not chord:
            self.show_info_popup("Por favor, insira um acorde")
            return

        if not re.match(r'^[A-G][#b]?(m|maj|min|dim|aug|\d|sus|add)?[0-9]*(\/[A-G][#b]?)?$', chord, re.IGNORECASE):
            self.show_info_popup(f"Formato de acorde inválido: {chord}")
            return

        new_text = text[:cursor_index] + f"[{chord}]" + text[cursor_index:]
        insertion_length = len(chord) + 2

        updated_metadata = {}
        for key, meta in self.chord_metadata.items():
            old_pos = int(key.split('_')[1])
            if old_pos >= cursor_index:
                new_pos = old_pos + insertion_length
                new_key = f"pos_{new_pos}"
                updated_metadata[new_key] = meta
            else:
                updated_metadata[key] = meta

        self.chord_metadata = updated_metadata
        self.ids.lyrics_input.text = new_text
        self.ids.lyrics_input.cursor = (cursor_index + insertion_length, 0)

        new_key = f"pos_{cursor_index}"
        if degree or comment:
            self.chord_metadata[new_key] = {
                "chord": chord,
                "degree": degree,
                "comment": comment
            }

        self.parse_chords()
        self.ids.chord_input.text = ""

    def parse_chords(self):
        current_selection = self.selected_occurrence
        current_button = self.selected_button
        
        text = self.ids.lyrics_input.text
        pattern = r'\[([A-G][#b]?(?:m|maj|min|dim|aug|\d|sus|add)?[0-9]*(?:\/[A-G][#b]?)?)\]'
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        
        temp_metadata_map = {}
        for key, meta in self.chord_metadata.items():
            if 'chord' in meta:
                chord = meta['chord']
                if chord not in temp_metadata_map:
                    temp_metadata_map[chord] = []
                if key.startswith('pos_'):
                    pos = int(key.split('_')[1])
                    line_number = text.count('\n', 0, pos) + 1
                    line_start = text.rfind('\n', 0, pos) + 1
                    line_text = text[line_start:text.find('\n', line_start)]
                    line_chord_pos = len(re.findall(
                        r'\[([A-G][#b]?(?:m|maj|min|dim|aug|\d|sus|add)?[0-9]*(?:\/[A-G][#b]?)?)\]', 
                        line_text[:pos-line_start])) + 1
                    temp_metadata_map[chord].append({
                        'meta': meta,
                        'line_number': line_number,
                        'line_chord_pos': line_chord_pos
                    })
                else:
                    temp_metadata_map[chord].append({'meta': meta})
        
        new_metadata = {}
        new_positions = []
        chord_counter = 1
        
        for match in matches:
            pos = match.start()
            chord = match.group(1)
            new_key = f"pos_{pos}"
            line_number = text.count('\n', 0, pos) + 1
            line_start = text.rfind('\n', 0, pos) + 1
            line_text = text[line_start:text.find('\n', line_start)]
            line_chord_pos = len(re.findall(
                r'\[([A-G][#b]?(?:m|maj|min|dim|aug|\d|sus|add)?[0-9]*(?:\/[A-G][#b]?)?)\]', 
                line_text[:pos-line_start])) + 1
            
            found_meta = None
            old_key = f"pos_{pos}"
            if old_key in self.chord_metadata and self.chord_metadata[old_key].get('chord') == chord:
                found_meta = self.chord_metadata[old_key]
            else:
                if chord in temp_metadata_map:
                    for candidate in temp_metadata_map[chord]:
                        if ('line_number' in candidate and 
                            candidate['line_number'] == line_number and 
                            candidate['line_chord_pos'] == line_chord_pos):
                            found_meta = candidate['meta']
                            temp_metadata_map[chord].remove(candidate)
                            break
                    
                    if not found_meta and temp_metadata_map[chord]:
                        found_meta = temp_metadata_map[chord].pop(0)['meta']
            
            if found_meta:
                new_metadata[new_key] = {
                    "chord": chord,
                    "degree": found_meta.get("degree", ""),
                    "comment": found_meta.get("comment", "")
                }
            else:
                new_metadata[new_key] = {"chord": chord, "degree": "", "comment": ""}
            
            new_positions.append(pos)
            self.chord_counter_map[new_key] = chord_counter
            chord_counter += 1
        
        self.chord_positions = new_positions
        self.chord_metadata = new_metadata
        self.cleanup_metadata()
        
        if current_selection in self.chord_metadata:
            self.selected_occurrence = current_selection
            if current_button and current_button.parent is self.ids.chord_list:
                self.selected_button = current_button
            else:
                self.selected_button = None
        else:
            self.selected_occurrence = ""
            self.selected_button = None
            self.clear_metadata_fields()
        
        self.ids.cifra_preview.text = self.get_colored_text(text, matches)
        self.ids.metadata_preview.text = self.build_chord_metadata_preview(matches)
        self.update_chord_buttons()
        self.update_selected_chord_label()

    def cleanup_metadata(self):
        text = self.ids.lyrics_input.text
        current_positions = [f"pos_{pos}" for pos in self.chord_positions]
        
        if self.selected_occurrence and self.selected_occurrence not in current_positions:
            self.selected_occurrence = ""
            if self.selected_button and self.selected_button.parent is self.ids.chord_list:
                meta = self.chord_metadata.get(self.selected_occurrence, {})
                has_metadata = meta.get("degree") or meta.get("comment")
                if has_metadata:
                    self.selected_button.background_color = (0.4, 0.9, 0.4, 1)
                else:
                    self.selected_button.background_color = (0.7, 0.7, 0.7, 1)
            self.selected_button = None
            self.clear_metadata_fields()
        
        metadata_keys = list(self.chord_metadata.keys())
        for key in metadata_keys:
            if key.startswith('pos_') and key not in current_positions:
                pos = int(key.split('_')[1])
                if pos < len(text) and text[pos] == '[':
                    match = re.match(
                        r'\[([A-G][#b]?(?:m|maj|min|dim|aug|\d|sus|add)?[0-9]*(?:\/[A-G][#b]?)?)\]', 
                        text[pos:pos+20])
                    if match:
                        continue
                del self.chord_metadata[key]

    def update_selected_chord_label(self):
        if not self.selected_occurrence:
            self.ids.selected_chord_label.text = "[i]Nenhum acorde selecionado[/i]"
            return
        
        key = self.selected_occurrence
        data = self.chord_metadata.get(key, {})
        chord = data.get("chord", "")
        if not chord:
            self.ids.selected_chord_label.text = "[i]Nenhum acorde selecionado[/i]"
            return
        
        pos = int(key.split('_')[1])
        text = self.ids.lyrics_input.text
        line_number = text.count('\n', 0, pos) + 1
        line_start = text.rfind('\n', 0, pos) + 1
        line_chord_pos = len(re.findall(
            r'\[([A-G][#b]?(?:m|maj|min|dim|aug|\d|sus|add)?[0-9]*(?:\/[A-G][#b]?)?)\]', 
            text[line_start:pos])) + 1
        chord_number = self.chord_counter_map.get(key, 0)
        display_text = f"[b]Acorde selecionado:[/b] #{chord_number} (L{line_number}-{line_chord_pos}) {chord}"
        self.ids.selected_chord_label.text = display_text

    def update_chord_buttons(self, *args):
        if self.selected_button and self.selected_button.parent is None:
            self.selected_button = None
            self.selected_occurrence = ""
        
        text = self.ids.lyrics_input.text
        self.ids.chord_list.clear_widgets()
        
        if not self.chord_positions:
            self.selected_button = None
            self.selected_occurrence = ""
            return

        line_chord_counts = {}
        
        for idx, pos in enumerate(self.chord_positions):
            match = re.match(
                r'\[([A-G][#b]?(?:m|maj|min|dim|aug|\d|sus|add)?[0-9]*(?:\/[A-G][#b]?)?)\]', 
                text[pos:pos+20])
            if not match:
                continue
                
            chord = match.group(1)
            key = f"pos_{pos}"
            line_number = text.count('\n', 0, pos) + 1
            
            if line_number not in line_chord_counts:
                line_chord_counts[line_number] = 1
            else:
                line_chord_counts[line_number] += 1
                
            line_chord_position = line_chord_counts[line_number]
            chord_number = idx + 1

            meta = self.chord_metadata.get(key, {"chord": chord, "degree": "", "comment": ""})
            
            btn_text = f"#{chord_number} (L{line_number}-{line_chord_position}) {chord}"
            
            is_selected = (key == self.selected_occurrence)
            has_metadata = meta["degree"] or meta["comment"]
            
            if is_selected and has_metadata:
                bg_color = (0.1, 0.6, 0.1, 1)
                text_color = (1, 1, 1, 1)
            elif is_selected and not has_metadata:
                bg_color = (0.1, 0.3, 0.7, 1)
                text_color = (1, 1, 1, 1)
            elif not is_selected and has_metadata:
                bg_color = (0.4, 0.9, 0.4, 1)
                text_color = (0, 0, 0, 1)
            else:
                bg_color = (0.7, 0.7, 0.7, 1)
                text_color = (0, 0, 0, 1)
            
            btn = Button(
                text=btn_text,
                size_hint_y=None,
                height=40,
                background_color=bg_color,
                color=text_color,
                font_size='14sp',
                halign='left',
                padding=[10, 0],
                background_normal='',
                bold=True
            )
            btn.bind(on_release=lambda btn, k=key: self.select_chord(k, btn))
            self.ids.chord_list.add_widget(btn)

    def select_chord(self, key, button):
        if not key or key not in self.chord_metadata:
            self.selected_occurrence = ""
            self.selected_button = None
            self.clear_metadata_fields()
            self.update_selected_chord_label()
            return

        if self.selected_button:
            meta = self.chord_metadata.get(self.selected_occurrence, {})
            has_metadata = meta.get("degree") or meta.get("comment")
            
            if has_metadata:
                self.selected_button.background_color = (0.4, 0.9, 0.4, 1)
                self.selected_button.color = (0, 0, 0, 1)
            else:
                self.selected_button.background_color = (0.7, 0.7, 0.7, 1)
                self.selected_button.color = (0, 0, 0, 1)
        
        self.selected_button = button
        self.selected_occurrence = key
        
        current_meta = self.chord_metadata.get(key, {})
        has_metadata = current_meta.get("degree") or current_meta.get("comment")
        
        if has_metadata:
            button.background_color = (0.1, 0.6, 0.1, 1)
        else:
            button.background_color = (0.1, 0.3, 0.7, 1)
        
        button.color = (1, 1, 1, 1)
        
        self.update_selected_chord_label()
        self.ids.degree_input.text = current_meta.get("degree", "")
        self.ids.comment_input.text = current_meta.get("comment", "")

    def update_metadata(self):
        if not self.selected_occurrence:
            return
            
        key = self.selected_occurrence
        if key in self.chord_metadata:
            self.chord_metadata[key]["degree"] = self.ids.degree_input.text
            self.chord_metadata[key]["comment"] = self.ids.comment_input.text
            
            if self.selected_button:
                pos = int(key.split('_')[1])
                text = self.ids.lyrics_input.text
                line_number = text.count('\n', 0, pos) + 1
                line_start = text.rfind('\n', 0, pos) + 1
                line_chord_pos = len(re.findall(
                    r'\[([A-G][#b]?(?:m|maj|min|dim|aug|\d|sus|add)?[0-9]*(?:\/[A-G][#b]?)?)\]', 
                    text[line_start:pos])) + 1
                chord_number = self.chord_counter_map.get(key, 0)
                chord = self.chord_metadata[key]["chord"]
                
                self.selected_button.text = f"#{chord_number} (L{line_number}-{line_chord_pos}) {chord}"
                
                has_metadata = self.ids.degree_input.text or self.ids.comment_input.text
                if has_metadata:
                    self.selected_button.background_color = (0.1, 0.6, 0.1, 1)
                else:
                    self.selected_button.background_color = (0.1, 0.3, 0.7, 1)
            
            self.update_selected_chord_label()
            self.parse_chords()

    def clear_metadata_fields(self):
        self.ids.degree_input.text = ""
        self.ids.comment_input.text = ""

    def get_colored_text(self, text, matches):
        offset = 0
        for match in matches:
            chord = match.group(1)
            start, end = match.span()
            key = f"pos_{start}"
            meta = self.chord_metadata.get(key, {"degree": "", "comment": ""})

            color = "#0000FF" if (meta["degree"].strip() or meta["comment"].strip()) else "#FF0000"
            color_tag = f"[color={color}][b][{chord}][/b][/color]"
            text = text[:start + offset] + color_tag + text[end + offset:]
            offset += len(color_tag) - (end - start)
        return text

    def build_chord_metadata_preview(self, matches):
        output = []
        for match in matches:
            chord = match.group(1)
            pos = match.start()
            key = f"pos_{pos}"
            meta = self.chord_metadata.get(key, {})
            grau = meta.get("degree", "").strip()
            comentario = meta.get("comment", "").strip()
            linha = f"[b]{chord}[/b] ({grau}) - {comentario}" if grau or comentario else f"[b]{chord}[/b] - (sem anotações)"
            output.append(linha)
        return "\n".join(output)

    def save_project(self):
        data = {
            "title": self.ids.project_title_input.text.strip() or "Sem título",
            "key": self.ids.project_key_input.text.strip(),
            "description": self.ids.project_description_input.text.strip(),
            "lyrics_text": self.ids.lyrics_input.text,
            "chord_metadata": self.chord_metadata
        }

        default_filename = (
            data["title"].strip().replace(" ", "_")
        ) + ".harmonia.json"

        def write_to_path(folder_path):
            try:
                path = Path(folder_path) / default_filename
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self.last_used_dir = str(Path(folder_path))
                self.show_info_popup(f"Projeto salvo com sucesso em:\n{path}")
            except Exception as e:
                self.show_info_popup(f"Erro ao salvar:\n{str(e)}")

        # Usa o último diretório ou o padrão se não existir
        initial_path = self.last_used_dir if Path(self.last_used_dir).exists() else self.default_dir
        self.show_directory_chooser(write_to_path, initial_path=initial_path)

    def load_project(self):
        def load_from_file(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self.ids.project_title_input.text = data.get("title", "Sem título")
                self.ids.project_key_input.text = data.get("key", "")
                self.ids.project_description_input.text = data.get("description", "")
                self.ids.lyrics_input.text = data.get("lyrics_text", "")
                self.chord_metadata = data.get("chord_metadata", {})
                self.selected_button = None
                self.selected_occurrence = ""
                self.ids.selected_chord_label.text = "[i]Nenhum acorde selecionado[/i]"
                self.last_used_dir = str(Path(path).parent)
                self.parse_chords()
                self.show_info_popup("Projeto carregado com sucesso!")
            except json.JSONDecodeError:
                self.show_info_popup("Erro: O arquivo não é um projeto válido")
            except Exception as e:
                self.show_info_popup(f"Erro ao carregar:\n{str(e)}")

        # Usa o último diretório ou o padrão se não existir
        initial_path = self.last_used_dir if Path(self.last_used_dir).exists() else self.default_dir
        self.show_file_chooser(load_from_file, save=False, initial_path=initial_path)

    def show_directory_chooser(self, callback, initial_path=None):
        chooser = FileChooserIconView(
            path=initial_path if initial_path else ".",
            dirselect=True
        )
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(chooser)

        confirm = Button(text="Salvar nesta pasta", size_hint_y=0.1)
        layout.add_widget(confirm)

        popup = Popup(
            title="Escolher pasta para salvar",
            content=layout,
            size_hint=(0.9, 0.9)
        )

        def _confirm(*args):
            if chooser.selection:
                popup.dismiss()
                callback(chooser.selection[0])

        confirm.bind(on_press=_confirm)
        popup.open()

    def show_file_chooser(self, callback, save=False, initial_path=None):
        chooser = FileChooserIconView(
            path=initial_path if initial_path else ".",
            filters=["*.harmonia.json", "*.json"]
        )
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(chooser)

        confirm = Button(
            text="Salvar aqui" if save else "Carregar", 
            size_hint_y=0.1
        )
        layout.add_widget(confirm)

        popup = Popup(
            title="Salvar projeto" if save else "Carregar projeto",
            content=layout,
            size_hint=(0.9, 0.9)
        )

        def _confirm(*args):
            if chooser.selection:
                popup.dismiss()
                callback(chooser.selection[0])

        confirm.bind(on_press=_confirm)
        popup.open()

    def show_info_popup(self, message):
        popup = Popup(
            title="Informação",
            content=Label(text=message),
            size_hint=(0.7, 0.5)
        )
        popup.open()

    def fetch_lyrics_from_letras(self):
        title = self.ids.project_title_input.text.strip().title()
        artist = self.ids.project_description_input.text.strip()

        if not title or not artist:
            self.show_info_popup("Por favor, preencha o título e o compositor para buscar a letra.")
            return

        try:
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept-Language": "pt-BR,pt;q=0.9"
            }

            # Processar o nome do artista para a URL
            artist_slug = (
                artist.strip()
                .lower()
                .replace(" ", "-")
                .replace("'", "")
                .replace("á", "a").replace("à", "a").replace("ã", "a").replace("â", "a")
                .replace("é", "e").replace("ê", "e")
                .replace("í", "i").replace("î", "i")
                .replace("ó", "o").replace("ô", "o").replace("õ", "o")
                .replace("ú", "u").replace("û", "u")
                .replace("ç", "c")
            )
            
            # Tentar diferentes variações da URL do artista
            artist_urls = [
                f"https://www.letras.com/{artist_slug}/",
                f"https://www.letras.com/{artist_slug}-mc/",
                f"https://www.letras.com/{artist_slug}-banda/",
                f"https://www.letras.com/{artist_slug}-musica/",
            ]

            response = None
            for url in artist_urls:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        artist_url = url
                        break
                except requests.RequestException:
                    continue

            if not response or response.status_code != 200:
                self.show_info_popup("Artista não encontrado no letras.com.")
                return

            soup = BeautifulSoup(response.text, "html.parser")

            # Encontra todos os links de músicas
            song_links = soup.find_all("a", title=True)

            # Compara títulos por similaridade
            def similarity(a, b):
                return SequenceMatcher(None, a.lower(), b.lower()).ratio()

            best_match = None
            best_score = 0.0

            for link in song_links:
                candidate = link.get("title")
                if candidate:
                    score = similarity(title, candidate)
                    if score > best_score:
                        best_score = score
                        best_match = link

            if not best_match or best_score < 0.6:
                self.show_info_popup("Música não encontrada ou muito diferente do título fornecido.")
                return

            lyrics_url = "https://www.letras.com" + best_match["href"]
            lyrics_response = requests.get(lyrics_url, headers=headers)

            if lyrics_response.status_code != 200:
                self.show_info_popup("Erro ao acessar a página da música.")
                return

            lyrics_soup = BeautifulSoup(lyrics_response.text, "html.parser")
            lyrics_div = lyrics_soup.find("div", class_="lyric-original")

            if not lyrics_div:
                self.show_info_popup("Letra não encontrada.")
                return

            lyrics = lyrics_div.get_text(separator="\n", strip=True)

            if lyrics.strip():
                self.ids.lyrics_input.text = lyrics
                self.show_info_popup(f"Letra carregada com sucesso!\nTítulo mais próximo encontrado:\n{best_match.get('title')}")
            else:
                self.show_info_popup("Letra encontrada, mas está vazia.")

        except Exception as e:
            self.show_info_popup(f"Erro inesperado:\n{str(e)}")

    def reset_all_fields(self):
        """Reseta todos os campos do projeto para os valores padrão"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(
            text="Tem certeza que deseja resetar todos os campos?\nTodos os dados não salvos serão perdidos."
        ))
        
        btn_layout = BoxLayout(spacing=5, size_hint_y=0.3)
        btn_yes = Button(text="Sim", background_color=(0.8, 0.3, 0.3, 1))
        btn_no = Button(text="Cancelar", background_color=(0.2, 0.6, 0.35, 1))
        btn_layout.add_widget(btn_no)
        btn_layout.add_widget(btn_yes)
        
        content.add_widget(btn_layout)
        
        popup = Popup(
            title="Confirmar Reset",
            content=content,
            size_hint=(0.7, 0.4)
        )
        
        def confirm_reset(instance):
            self.ids.project_title_input.text = ""
            self.ids.project_description_input.text = ""
            self.ids.project_key_input.text = ""
            self.ids.lyrics_input.text = ""
            self.ids.chord_input.text = ""
            self.chord_metadata = {}
            self.selected_occurrence = ""
            self.selected_button = None
            self.chord_positions = []
            self.chord_counter_map = {}
            self.ids.degree_input.text = ""
            self.ids.comment_input.text = ""
            self.ids.selected_chord_label.text = "[i]Nenhum acorde selecionado[/i]"
            self.ids.cifra_preview.text = ""
            self.ids.metadata_preview.text = ""
            self.ids.chord_list.clear_widgets()
            
            popup.dismiss()
            self.show_info_popup("Todos os campos foram resetados com sucesso!")
        
        btn_yes.bind(on_press=confirm_reset)
        btn_no.bind(on_press=popup.dismiss)
        
        popup.open()

class HarmonyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_screen = None
        self.splash = None
        self.splash_duration = 3.0

    def build(self):
        self.title = "Harmonauta"
        self.icon = "harmonauta_logo.png"
        self.splash = SplashScreen()
        Clock.schedule_once(self.build_main_interface, 0.1)
        self.root = FloatLayout()
        self.root.add_widget(self.splash)
        return self.root
    
    def build_main_interface(self, dt):
        if hasattr(self.splash, 'label'):  # Verificação segura
            self.splash.label.text = "Carregando recursos..."
        
        self.main_screen = HarmonyScreen()
        Clock.schedule_once(self.show_main_interface, max(0.1, self.splash_duration - 0.6))
    
    def show_main_interface(self, dt):
        self.root.clear_widgets()
        self.root.add_widget(self.main_screen)
        self.splash = None

if __name__ == "__main__":
    HarmonyApp().run()