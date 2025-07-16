from PIL import Image, ImageDraw, ImageFont
import os

ImageType = Image.Image

PRINT_ORDER = "HPIJGOABFEKCNMLD"

REGULAR_CARD = [
    "ABNM",
    "PCOD",
    "IJFE",
    "HKGL"
]

def new_card(width: int = 300, height: int = 300, grid_order: str = PRINT_ORDER) -> ImageType:
    """Create a new card image with a 4x4 grid of tiles."""
    grid = Image.new('RGBA', (width * 4, height * 4), color='white')
    draw = ImageDraw.Draw(grid)
    font_size = min(width, height) * 0.6
    # load a monotype font
    font = ImageFont.truetype("Courier New.ttf", int(font_size))
    for i in range(4):
        for j in range(4):
            letter = grid_order[i * 4 + j]
            draw.text((j * width + font_size / 2, i * height + font_size / 3), letter, fill='black', font=font, align='center')
            # draw border around each tile
            draw.rectangle([j * width, i * height, (j + 1) * width, (i + 1) * height], outline='green', width=2)
    return grid

def to_faces(grid: Image, grid_order: str = PRINT_ORDER, face_order: list[str] = REGULAR_CARD) -> list[ImageType]:
    """Convert a 4x4 grid image to 2x2 faces."""
    faces = []
    for face in face_order:
        face_image = Image.new('RGBA', (grid.width // 2, grid.height // 2), color='white')
        draw = ImageDraw.Draw(face_image)
        for i in range(2):
            for j in range(2):
                letter = face[i * 2 + j]
                x = grid_order.index(letter) % 4
                y = grid_order.index(letter) // 4

                tile = grid.crop((x * (grid.width // 4), y * (grid.height // 4), (x + 1) * (grid.width // 4), (y + 1) * (grid.height // 4)))
                face_image.paste(tile, (j * (face_image.width // 2), i * (face_image.height // 2)))
        faces.append(face_image)
    return faces

def to_grid(faces: list[ImageType], grid_order: str = PRINT_ORDER, face_order: list[str] = REGULAR_CARD) -> ImageType:
    """Convert a list of 2x2 faces back to a 4x4 grid image."""
    grid = Image.new('RGBA', (faces[0].width * 2, faces[0].height * 2), color='white')
    for i, face in enumerate(face_order):
        face_image = faces[i]
        for j in range(2):
            for k in range(2):
                letter = face[j * 2 + k]
                x = grid_order.index(letter) % 4
                y = grid_order.index(letter) // 4
                grid.paste(face_image.crop((k * (face_image.width // 2), j * (face_image.height // 2), (k + 1) * (face_image.width // 2), (j + 1) * (face_image.height // 2))), 
                                          (x * (face_image.width // 2), y * (face_image.height // 2)))
    return grid

def new_card_subdirectory(path: str, width: int = 300, height: int = 300) -> None   :
    """Create a new subdirectory for card images."""
    if not os.path.exists(path):
        os.makedirs(path)

    grid = new_card(width, height)
    grid.save(os.path.join(path, 'grid.png'))
    faces = to_faces(grid)
    for i, face in enumerate(faces):
        face.save(os.path.join(path, f'face{i + 1}.png'))

    new_grid = to_grid(faces)
    new_grid.save(os.path.join(path, 'new_grid.png'))


def main():
    print("Hello from shuffler!")
    new_card_subdirectory('./test', width = 500, height = 500)

if __name__ == "__main__":
    main()
