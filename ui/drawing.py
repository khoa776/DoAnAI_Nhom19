def draw_text(surface, text, font, color, pos):
    surface.blit(font.render(text, True, color), pos)


def draw_center(surface, text, font, color, rect):
    img = font.render(text, True, color)
    surface.blit(img, img.get_rect(center=rect.center))


def wrap_text(text, font, width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = word if not current else current + " " + word
        if font.size(test)[0] <= width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines
