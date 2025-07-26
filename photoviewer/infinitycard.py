from PIL import Image, ImageDraw, ImageFont
import os
from typing import List

ImageType = Image.Image

PRINT_ORDER = "HPIJGOABFEKCNMLD"

REGULAR_CARD = [
    "ABNM",
    "PCOD",
    "IJFE",
    "HKGL"
]

CLOCKWISE_CARD = [
    "ABFD",
    "HCFD",
    "HJFE",
    "HJGL",
    "IJNL",
    "PKNL",
    "PBNM",
    "PBOD"
]

class InfinityCardProject:
    def __init__(self, name: str, path: str, width: int = 300, height: int = 300,
                 grid_order: str = PRINT_ORDER, face_order: List[str] = CLOCKWISE_CARD):
        self.name = name
        self.path = path
        self.width = width
        self.height = height
        self.grid_order = grid_order
        self.face_order = face_order
        self.grid: ImageType | None = None
        self.faces: List[ImageType] = []

        os.makedirs(self.path, exist_ok=True)
        self.load_or_create_project()

    def load_or_create_project(self):
        grid_path = os.path.join(self.path, "grid.png")
        if os.path.exists(grid_path):
            self.load_images()
        else:
            self.create_images()

    def create_images(self):
        print(f"[{self.name}] Creating new images...")
        self.grid = self._new_card()
        self.grid.save(os.path.join(self.path, "grid.png"))

        self.faces = self._to_faces(self.grid)
        for i, face in enumerate(self.faces):
            face.save(os.path.join(self.path, f"face{i + 1}.png"))

    def load_images(self):
        print(f"[{self.name}] Loading images from disk...")
        self.grid = Image.open(os.path.join(self.path, "grid.png"))
        self.faces = []
        for i in range(len(self.face_order)):
            face_path = os.path.join(self.path, f"face{i + 1}.png")
            if os.path.exists(face_path):
                self.faces.append(Image.open(face_path))
            else:
                raise FileNotFoundError(f"Missing face image: {face_path}")

    def update_face(self, face_filename: str):
        """Update the grid with a modified face image and regenerate all faces."""
        face_path = os.path.join(self.path, face_filename)
        if not os.path.exists(face_path):
            raise FileNotFoundError(f"Face file not found: {face_path}")

        face_image = Image.open(face_path)
        index_str = os.path.splitext(face_filename)[0].replace("face", "")
        if not index_str.isdigit():
            raise ValueError(f"Invalid face filename format: {face_filename}")
        face_index = int(index_str) - 1
        if not (0 <= face_index < len(self.face_order)):
            raise IndexError(f"Face index out of range: {face_index}")

        face_code = self.face_order[face_index]
        tile_w = face_image.width // 2
        tile_h = face_image.height // 2

        for i in range(2):
            for j in range(2):
                letter = face_code[i * 2 + j]
                x = self.grid_order.index(letter) % 4
                y = self.grid_order.index(letter) // 4
                tile = face_image.crop((j * tile_w, i * tile_h, (j + 1) * tile_w, (i + 1) * tile_h))
                self.grid.paste(tile, (x * tile_w, y * tile_h))

        # Save updated grid
        self.grid.save(os.path.join(self.path, "grid.png"))

        # Regenerate and save all faces
        self.faces = self._to_faces(self.grid)
        for i, face in enumerate(self.faces):
            face.save(os.path.join(self.path, f"face{i + 1}.png"))

        print(f"[{self.name}] Updated grid and faces from {face_filename}")

    def _new_card(self) -> ImageType:
        grid = Image.new('RGBA', (self.width * 4, self.height * 4), color='white')
        draw = ImageDraw.Draw(grid)
        font_size = min(self.width, self.height) * 0.6

        try:
            font = ImageFont.truetype("Courier New.ttf", int(font_size))
        except OSError:
            font = ImageFont.load_default()
            print("Warning: 'Courier New.ttf' not found. Using default font.")

        for i in range(4):
            for j in range(4):
                letter = self.grid_order[i * 4 + j]
                # Centered text
                text_bbox = draw.textbbox((0, 0), letter, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                x = j * self.width + (self.width - text_width) / 2
                y = i * self.height + (self.height - text_height) / 2
                draw.text((x, y), letter, fill='black', font=font)
                draw.rectangle([j * self.width, i * self.height, (j + 1) * self.width, (i + 1) * self.height], outline='green', width=2)
        return grid

    def _to_faces(self, grid: ImageType) -> List[ImageType]:
        faces = []
        for face in self.face_order:
            face_image = Image.new('RGBA', (grid.width // 2, grid.height // 2), color='white')
            for i in range(2):
                for j in range(2):
                    letter = face[i * 2 + j]
                    x = self.grid_order.index(letter) % 4
                    y = self.grid_order.index(letter) // 4
                    tile = grid.crop((x * (grid.width // 4), y * (grid.height // 4), 
                                      (x + 1) * (grid.width // 4), (y + 1) * (grid.height // 4)))
                    face_image.paste(tile, (j * (face_image.width // 2), i * (face_image.height // 2)))
            faces.append(face_image)
        return faces

    def _to_grid(self, faces: List[ImageType]) -> ImageType:
        grid = Image.new('RGBA', (faces[0].width * 2, faces[0].height * 2), color='white')
        for i, face in enumerate(self.face_order):
            face_image = faces[i]
            for j in range(2):
                for k in range(2):
                    letter = face[j * 2 + k]
                    x = self.grid_order.index(letter) % 4
                    y = self.grid_order.index(letter) // 4
                    tile = face_image.crop((k * (face_image.width // 2), j * (face_image.height // 2), 
                                            (k + 1) * (face_image.width // 2), (j + 1) * (face_image.height // 2)))
                    grid.paste(tile, (x * (face_image.width // 2), y * (face_image.height // 2)))
        return grid

