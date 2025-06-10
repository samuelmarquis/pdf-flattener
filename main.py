import numpy as np
import math
from PIL import Image, ImageDraw, ImageFont
from sys import argv
from poppler import load_from_file, PageRenderer


def create_image_grid(
	images: list[Image.Image],
	target_aspect_ratio: float,
	margin: int = 10,
	bg_color: str = "white"
) -> Image.Image | None:
	if not images:
		print("Warning: The input list of images is empty.")
		return None

	iw, ih = images[0].size
	if iw == 0 or ih == 0:
		raise ValueError("Input images must have non-zero dimensions.")

	image_aspect_ratio = iw / ih

	num_images = len(images)
	cols, rows = _calculate_grid_layout(num_images, image_aspect_ratio, target_aspect_ratio)

	print(f"Input: {num_images} images ({iw}x{ih})")
	print(f"Target Aspect Ratio: {target_aspect_ratio:.2f}")
	print(f"Optimal Grid Layout: {cols} columns x {rows} rows")

	gw = (cols * iw) + (cols + 1) * margin
	gh = (rows * ih) + (rows + 1) * margin

	canvas = Image.new('RGB', (gw, gh), color=bg_color)

	for i, image in enumerate(images):
		row = i // cols
		col = i % cols

		x_offset = margin + col * (iw + margin)
		y_offset = margin + row * (ih + margin)

		canvas.paste(image, (x_offset, y_offset))

	return canvas

def _calculate_grid_layout(num_images: int, image_aspect_ratio: float, target_aspect_ratio: float) -> tuple[int, int]:
	best_layout = (0, 0)
	min_diff = float('inf')

	grid_shape_ratio = target_aspect_ratio / image_aspect_ratio

	for cols in range(1, num_images + 1):
		rows = math.ceil(num_images / cols)
		current_ratio = cols / rows
		diff = abs(current_ratio - grid_shape_ratio)

		if diff < min_diff:
			min_diff = diff
			best_layout = (cols, rows)
			
	return best_layout

if __name__ == "__main__":
	if len(argv) != 3:
		print("Pass a .pdf file and a directory to write the resulting image")
	outloc = argv[2]

	pdf = load_from_file(argv[1])
	images = []
	renderer = PageRenderer()
	n_pages = pdf.pages
	for i in range(0, n_pages):
		page = pdf.create_page(i)
		image = renderer.render_page(page, xres=250, yres=250)
		pil_image = Image.frombytes(
			"RGBA",
			(image.width, image.height),
			image.data,
			"raw",
			str(image.format),
		)
		images.append(pil_image)

	TARGET_GRID_ASPECT_RATIO = 16 / 9

	final_grid = create_image_grid(
		images=images,
		target_aspect_ratio=TARGET_GRID_ASPECT_RATIO,
		margin=20,
		bg_color="#333333"
	)

	if final_grid:
		output_filename = outloc + "image_grid.png"
		final_grid.save(output_filename)
		print("Success")
