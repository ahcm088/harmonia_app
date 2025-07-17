import json
import re
import traceback
from pathlib import Path
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import DictProperty, StringProperty, ListProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.label import Label

try:
    Builder.load_file("app/ui.kv")
except Exception as e:
    print(f"Erro crítico ao carregar o arquivo KV: {e}")
    traceback.print_exc()
    raise SystemExit("Não foi possível carregar a interface. O aplicativo será encerrado.")

class HarmonyScreen(BoxLayout):
    selected_occurrence = StringProperty("")
    chord_metadata = DictProperty({})
    project_title = StringProperty("Sem título")
    chord_positions = ListProperty([])
    chord_counter_map = DictProperty({})
    selected_button = ObjectProperty(None, allownone=True)
    last_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(chord_positions=self.update_chord_buttons)

    def on_text_change(self, instance, value):
        """Chamado quando o texto da cifra é alterado"""
        if hasattr(self, 'last_text'):
            # Verificar se houve remoção de linhas
            old_lines = self.last_text.split('\n')
            new_lines = value.split('\n')
            
            # Se o número de linhas mudou significativamente, forçar reparse completo
            if len(new_lines) != len(old_lines):
                self.parse_chords()
                self.last_text = value
                return
            
            # Verificar se alguma linha foi completamente removida
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
        # Guardar a seleção atual antes de fazer o parse
        current_selection = self.selected_occurrence
        current_button = self.selected_button
        
        text = self.ids.lyrics_input.text
        pattern = r'\[([A-G][#b]?(?:m|maj|min|dim|aug|\d|sus|add)?[0-9]*(?:\/[A-G][#b]?)?)\]'
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        
        # Criar mapeamento mais inteligente de acordes para metadados
        temp_metadata_map = {}
        for key, meta in self.chord_metadata.items():
            if 'chord' in meta:
                chord = meta['chord']
                if chord not in temp_metadata_map:
                    temp_metadata_map[chord] = []
                # Armazenar também o contexto (linha e posição relativa)
                if key.startswith('pos_'):
                    pos = int(key.split('_')[1])
                    line_number = text.count('\n', 0, pos) + 1
                    line_start = text.rfind('\n', 0, pos) + 1
                    line_text = text[line_start:text.find('\n', line_start)]
                    line_chord_pos = len(re.findall(r'\[([A-G][#b]?(?:m|maj|min|dim|aug|\d|sus|add)?[0-9]*(?:\/[A-G][#b]?)?)\]', 
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
            line_chord_pos = len(re.findall(r'\[([A-G][#b]?(?:m|maj|min|dim|aug|\d|sus|add)?[0-9]*(?:\/[A-G][#b]?)?)\]', 
                                          line_text[:pos-line_start])) + 1
            
            found_meta = None
            
            # Primeiro tentar encontrar pela posição exata (se ainda existe)
            old_key = f"pos_{pos}"
            if old_key in self.chord_metadata and self.chord_metadata[old_key].get('chord') == chord:
                found_meta = self.chord_metadata[old_key]
            else:
                # Se não encontrou pela posição, tentar pelo contexto (linha e posição na linha)
                if chord in temp_metadata_map:
                    for candidate in temp_metadata_map[chord]:
                        if ('line_number' in candidate and 
                            candidate['line_number'] == line_number and 
                            candidate['line_chord_pos'] == line_chord_pos):
                            found_meta = candidate['meta']
                            # Remover da lista para não reutilizar
                            temp_metadata_map[chord].remove(candidate)
                            break
                    
                    # Se ainda não encontrou, pegar o primeiro disponível (como fallback)
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
        
        # Restaurar a seleção se o acorde ainda existir
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
        """Remove metadados de acordes que não existem mais na cifra"""
        text = self.ids.lyrics_input.text
        current_positions = [f"pos_{pos}" for pos in self.chord_positions]
        
        # Verificar se o acorde selecionado ainda existe
        if self.selected_occurrence and self.selected_occurrence not in current_positions:
            self.selected_occurrence = ""
            if self.selected_button and self.selected_button.parent is self.ids.chord_list:
                # Resetar a cor do botão se ele ainda existir
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
                    match = re.match(r'\[([A-G][#b]?(?:m|maj|min|dim|aug|\d|sus|add)?[0-9]*(?:\/[A-G][#b]?)?)\]', 
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
            text[line_start:pos]
        )) + 1
        chord_number = self.chord_counter_map.get(key, 0)
        display_text = f"[b]Acorde selecionado:[/b] #{chord_number} (L{line_number}-{line_chord_pos}) {chord}"
        self.ids.selected_chord_label.text = display_text

    def update_chord_buttons(self, *args):
        # Limpar a referência se o botão não existir mais
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
            match = re.match(r'\[([A-G][#b]?(?:m|maj|min|dim|aug|\d|sus|add)?[0-9]*(?:\/[A-G][#b]?)?)\]', 
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
                bg_color = (0.1, 0.6, 0.1, 1)  # Verde escuro
                text_color = (1, 1, 1, 1)
            elif is_selected and not has_metadata:
                bg_color = (0.1, 0.3, 0.7, 1)   # Azul escuro
                text_color = (1, 1, 1, 1)
            elif not is_selected and has_metadata:
                bg_color = (0.4, 0.9, 0.4, 1)   # Verde claro
                text_color = (0, 0, 0, 1)
            else:
                bg_color = (0.7, 0.7, 0.7, 1)   # Cinza médio
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
            # Atualizar metadados
            self.chord_metadata[key]["degree"] = self.ids.degree_input.text
            self.chord_metadata[key]["comment"] = self.ids.comment_input.text
            
            # Atualizar o botão selecionado
            if self.selected_button:
                pos = int(key.split('_')[1])
                text = self.ids.lyrics_input.text
                line_number = text.count('\n', 0, pos) + 1
                line_start = text.rfind('\n', 0, pos) + 1
                line_chord_pos = len(re.findall(
                    r'\[([A-G][#b]?(?:m|maj|min|dim|aug|\d|sus|add)?[0-9]*(?:\/[A-G][#b]?)?)\]', 
                    text[line_start:pos]
                )) + 1
                chord_number = self.chord_counter_map.get(key, 0)
                chord = self.chord_metadata[key]["chord"]
                
                self.selected_button.text = f"#{chord_number} (L{line_number}-{line_chord_pos}) {chord}"
                
                has_metadata = self.ids.degree_input.text or self.ids.comment_input.text
                if has_metadata:
                    self.selected_button.background_color = (0.1, 0.6, 0.1, 1)
                else:
                    self.selected_button.background_color = (0.1, 0.3, 0.7, 1)
            
            # Forçar atualização da interface
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
                self.show_info_popup(f"Projeto salvo com sucesso em:\n{path}")
            except Exception as e:
                self.show_info_popup(f"Erro ao salvar:\n{str(e)}")

        self.show_directory_chooser(write_to_path)

    def load_project(self):
        def load_from_file(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self.ids.project_title_input.text = data.get("title", "Sem título")
                self.ids.lyrics_input.text = data.get("lyrics_text", "")
                self.chord_metadata = data.get("chord_metadata", {})
                self.selected_button = None
                self.selected_occurrence = ""
                self.ids.selected_chord_label.text = "[i]Nenhum acorde selecionado[/i]"
                self.parse_chords()
                self.show_info_popup("Projeto carregado com sucesso!")
            except json.JSONDecodeError:
                self.show_info_popup("Erro: O arquivo não é um projeto válido")
            except Exception as e:
                self.show_info_popup(f"Erro ao carregar:\n{str(e)}")

        self.show_file_chooser(load_from_file, save=False)

    def show_directory_chooser(self, callback):
        chooser = FileChooserIconView(path=".", dirselect=True)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(chooser)

        confirm = Button(text="Salvar nesta pasta", size_hint_y=0.1)
        layout.add_widget(confirm)

        popup = Popup(title="Escolher pasta para salvar",
                      content=layout,
                      size_hint=(0.9, 0.9))

        def _confirm(*args):
            if chooser.selection:
                popup.dismiss()
                callback(chooser.selection[0])

        confirm.bind(on_press=_confirm)
        popup.open()

    def show_file_chooser(self, callback, save=False):
        chooser = FileChooserIconView(path=".", filters=["*.harmonia.json", "*.json"])
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(chooser)

        confirm = Button(text="Salvar aqui" if save else "Carregar", size_hint_y=0.1)
        layout.add_widget(confirm)

        popup = Popup(title="Salvar projeto" if save else "Carregar projeto",
                      content=layout,
                      size_hint=(0.9, 0.9))

        def _confirm(*args):
            if chooser.selection:
                popup.dismiss()
                callback(chooser.selection[0])

        confirm.bind(on_press=_confirm)
        popup.open()

    def show_info_popup(self, message):
        popup = Popup(title="Informação",
                      content=Label(text=message),
                      size_hint=(0.7, 0.5))
        popup.open()


class HarmonyApp(App):
    def build(self):
        self.title = "Editor de Cifras"
        return HarmonyScreen()


if __name__ == "__main__":
    HarmonyApp().run()