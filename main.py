from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import DictProperty, StringProperty
from kivy.uix.button import Button
import re
import traceback

try:
    Builder.load_file("app/ui.kv")
except Exception:
    print("Erro ao carregar o arquivo KV:")
    traceback.print_exc()


class HarmonyScreen(BoxLayout):
    selected_occurrence = StringProperty("")
    chord_metadata = DictProperty({})  # Ex: {"pos_123": {"chord": "Am", "degree": "...", "comment": "..."}}

    def insert_chord_tag(self):
        cursor_index = self.ids.lyrics_input.cursor_index()
        text = self.ids.lyrics_input.text
        chord = self.ids.chord_input.text.strip()
        degree = self.ids.degree_input.text.strip()
        comment = self.ids.comment_input.text.strip()

        if not chord:
            return

        new_text = text[:cursor_index] + f"[{chord}]" + text[cursor_index:]
        self.ids.lyrics_input.text = new_text
        self.ids.lyrics_input.cursor = (cursor_index + len(chord) + 2, 0)

        # Criar metadado com dados atuais se houver grau ou comentário
        if degree or comment:
            pos = cursor_index
            key = f"pos_{pos}"
            self.chord_metadata[key] = {
                "chord": chord,
                "degree": degree,
                "comment": comment
            }

        # Atualizar preview imediatamente
        self.parse_chords()

    def parse_chords(self):
        text = self.ids.lyrics_input.text
        matches = list(re.finditer(r'\[([A-G][#b]?[a-zA-Z0-9+º°]*)\]', text))

        self.ids.chord_list.clear_widgets()
        self.ids.cifra_preview.text = self.get_colored_text(text, matches)

        # Remove metadados para acordes não mais existentes
        keys_to_keep = {f"pos_{m.start()}" for m in matches}
        self.chord_metadata = {k: v for k, v in self.chord_metadata.items() if k in keys_to_keep}

        for match in matches:
            chord = match.group(1)
            pos = match.start()
            key = f"pos_{pos}"

            # Se não existe metadado, criar vazio
            if key not in self.chord_metadata:
                self.chord_metadata[key] = {"chord": chord, "degree": "", "comment": ""}

            btn = Button(
                text=f"{chord} (pos {pos})",
                size_hint_y=None,
                height=40
            )
            btn.bind(on_release=lambda btn, k=key: self.select_chord(k))
            self.ids.chord_list.add_widget(btn)

    def select_chord(self, key):
        self.selected_occurrence = key
        data = self.chord_metadata.get(key, {})
        self.ids.degree_input.text = data.get("degree", "")
        self.ids.comment_input.text = data.get("comment", "")
        self.ids.selected_chord_label.text = f"[b]Ocorrência:[/b] {key}"

    def update_metadata(self):
        key = self.selected_occurrence
        if key in self.chord_metadata:
            self.chord_metadata[key]["degree"] = self.ids.degree_input.text
            self.chord_metadata[key]["comment"] = self.ids.comment_input.text
            # Atualizar preview para refletir a cor
            self.parse_chords()

    def clear_metadata_fields(self):
        self.ids.degree_input.text = ""
        self.ids.comment_input.text = ""

    def get_colored_text(self, text, matches):
        # Substitui os acordes por texto colorido
        offset = 0
        for match in matches:
            chord = match.group(1)
            start, end = match.span()
            key = f"pos_{start}"
            meta = self.chord_metadata.get(key, {"degree": "", "comment": ""})

            # Cor vermelha se grau e comentário vazios, azul caso contrário
            if meta["degree"].strip() or meta["comment"].strip():
                color = "#0000FF"  # azul
            else:
                color = "#FF0000"  # vermelho

            color_tag = f"[color={color}][b][{chord}][/b][/color]"
            text = text[:start + offset] + color_tag + text[end + offset:]
            offset += len(color_tag) - (end - start)
        return text


class HarmonyApp(App):
    def build(self):
        self.title = "Editor de Cifras"
        return HarmonyScreen()


if __name__ == "__main__":
    HarmonyApp().run()
