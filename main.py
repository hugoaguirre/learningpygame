## Con comentarios como este iré explicando lo que estoy haciendo en este juego,
## el código está en inglés y la explicación en espanol, espero que eso no cause
## problemas
##
## Si ya corriste el juego puedes ver que es un shooter muy sencillo, donde vas
## caminando por una especie de calabozo asesinando robots.
##
## El juego está escrito en python y pygame, que es una librería muy útil para
## el desarrollo de juegos. Pygame es una adaptación de una librería de multime
## dia escrita en C: SDL.
## Pygame nos va a dar utilerías para poder hacer nuetros juegos pero no es un
## framework, essto quiere decir que no nos impone una forma de estructurar el
## código, convenciones de nombres, métodos a implementar o cosas por el estilo
## tenemos simplemente una serie de utilerías que podemos usar como queramos pa
## ra interactuar con la multimedia, imágenes, sonido, dispositivos de entrada.

## La intención de este archivo main.py es inicializar lo que vamos a necesitar
## y cargar el menú del juego, vamos línea por línea

## Importamos primero pygame, de aquí en adelante podemos usar pygame.[modulo]
## para usar las utilidades de pygame.
import pygame
from os.path import join as path_join

## importamos después menu, que es la primer pantalla que vamos a mostrar
## argparse para parsear argumentos de la consola
## settings que tiene configuraciones del juego
## y constants que tiene valores que son útiles en todo el alcance del código
import menu
import argparse
from settings import settings
from constants import SCREEN_SIZE

## constants y settings son similares en el hecho de que están separados para
## que el acceso a los valores ahí dentro sea fácil desde cualquier archivo en
## el programa. La diferencia es que settings podemos modificar los valores de
## settings en cualquier lugar pero no podemos cambiar los valores de constants
## (en realidad no hay nada que nos impida cambiar los valores en constants,
## no hacerlo es un pacto entre los desarrolladores)

## la función main() es el punto de entrada de nuestro juego, simplemente toma
## los argumentos de la línea de comandos, inicializa los subsistemas de pygame
## [ver init_screen()] y muestra la primer pantalla: el menú
def main():
    args = parse_args()
    settings['debug'] = args.debug
    screen = init_screen()
    menu.MainMenu(screen)

## parse_args() utiliza argparse que es un módulo de python
## [https://docs.python.org/2/howto/argparse.html]
## por ahora solo tenemos un argumento, --debug, entre otras cosas nos hace in
## mortales (sólo en el juego)
def parse_args():
    parser = argparse.ArgumentParser(description='Sara is shooting some robots')
    parser.add_argument('--debug', help='Useful for debugging purposes', default=False, action='store_true')
    return parser.parse_args()

## init_screen inicializa subsistemas de pygame, la documentación de pygame dice
## que inicialicemos esto antes de usarlos
def init_screen():
    pygame.init()
    ## Ocultamos el puntero del mouse
    pygame.mouse.set_visible(0)
    ## Podemos un título en la ventana
    pygame.display.set_caption('Sara\'s shooter')
    ## Ponemos un ícono en la ventana
    pygame.display.set_icon(pygame.image.load(path_join('images', 'icon.png')))
    ## inicializamos el sonido
    pygame.mixer.pre_init(44100, -16, 2, 1024*4)
    ## iniciamos una pantalla, pygame.DOUBLEBUF hace que utilicemos una pantalla
    ## que usará la técnica de double buffer. Double buffering es una técnica u
    ## sada en gráficos para evitar que al actualizar la imágen en la pantalla
    ## se vea ese efecto de brinco, como que la pantalla no se actualiza por
    ## completo. Se utiliza un área de memoria RAM para 'dibujar' la siguiente
    ## pantalla, cuando está lista se copia a la V(ideo)RAM y así al no construir
    ## la imagen directamente en VRAM se evita el efecto mencionado
    ## [https://en.wikipedia.org/wiki/Multiple_buffering#Double_buffering_in_computer_graphics]
    return pygame.display.set_mode(SCREEN_SIZE, pygame.DOUBLEBUF)

if __name__ == '__main__':
    main()

## Para continuar ve a menu.py
