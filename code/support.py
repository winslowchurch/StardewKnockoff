from os import walk
import pygame

def import_folder(path):
    surface_list = []

    for _, _, img_files in walk(path):
        # Sort img_files to ensure correct order
        img_files.sort(reverse=True) 
        for image in img_files:
            full_path = path + '/' + image
            try:
                image_surf = pygame.image.load(full_path).convert_alpha()
                surface_list.append(image_surf)
            except pygame.error as e:
                print(f"Error loading image '{full_path}': {e}")

    return surface_list
