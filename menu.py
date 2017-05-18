import pygame
## ezmenu es una librería escrita usando pygame que muestra menus
## la copié de un clon de super mario que encontré en internet
## puedes ver el archivo ezmenu.py donde incluyo la licencia y la url
import ezmenu
from sys import exit as sys_exit

import game
from settings import settings
from constants import SCREEN_SIZE


## No explicaré clases y toda la sintaxis orientada a objetos
## a menos que haya algo interesante que explicar
class MainMenu:

    ## Muy importante, en main.py:main() pasé como screen la pantalla
    ## que inicializa pygame y atención se trata como una Surface donde podemos
    ## dibujar. Ese object lo iremos pasando de aquí a allá así que es importan
    ## te tenerlo en mente
    def __init__(self, screen):
        self.screen = screen
        ## ezmenu se inicializa con una serie de listas que actuan como opciones
        ## Primero está el texto que aparecerá en el menu
        ## el segundo elemento es la función que se ejecutará
        self.menu = ezmenu.EzMenu(
            ## lambda: crea una función sin nombre aquí mismo y la regresa como
            ## valor. Nota que no la ejecuta y la cree así para poder pasarle
            ## un argumento a game.py:game.Game() que es la función que comien
            ## za el juego
            ['Start', lambda: game.Game(screen)],
            ['Quit', sys_exit]
        )

        ## Configuraciones del menú
        self.menu.set_highlight_color((255, 0, 0))
        self.menu.set_normal_color((255, 255, 255))
        ## La primer operación geométrica del código, vamos a encontrarnos ins
        ## trucciones así muchas veces
        self.menu.center_at(SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2)
        self.menu.set_font(pygame.font.Font(settings['font'], 60))

        ## el reloj de pygame nos va a ayudar en este caso a limitar el framerate
        self.clock = pygame.time.Clock()

        ## ejecutamos la función principal para mostrar el menú
        self.main()

    def main(self):
        ## Estas dos líneas cargan la música y la reproduces
        pygame.mixer.music.load("music/menu.wav")
        ## -1 significa que se reproduzca infinitamente
        pygame.mixer.music.play(-1)

        ## while True
        ## Antes de programar un videojuego tenía algunas dudas de como funciona
        ## ban las cosas en su desarrollo. Esencialmente no sabía como comenzar
        ## a programar uno.
        ## El asunto está en saber que los juegos funcionan con un ciclo princi
        ## pal, como este, que lee entradas, calcula lo suyo y dibuja una nueva
        ## pantalla, una y otra vez... un montón de veces cada segundo, para ser
        ## específicos 30 veces por segundo en este juego
        ## Frente a ti está una versión simple de un ciclo principal que lo que
        ## hace es mostrar el menú esperando a que elijas una opción.
        ## Recuerda que el alma del juego es un ciclo como este dando vueltas sin
        ## parar redibujando la pantalla cada vez que termina una vuelta
        while True:
            ## Esto es precisamente lo que detiene el ciclo un poco para que de
            ## 30 vueltas cada segundo y evitar que en máquinas más potentes el
            ## juego sea más rápido que eso
            self.clock.tick(30)
            ## pygame.event.get() regresa los eventos que activo el usuario en
            ## este caso al menu le interesan los eventos del teclado, quizás
            ## el mouse también tendría que ver el código de la librería
            ## vamos a ver más sobre eventos una vez que entremos al código prin
            ## cipal
            events = pygame.event.get()
            self.menu.update(events)
            ## Aquí vamos a revisar si existe un evento especial que hace que
            ## cerremos la ventana
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()

            ## Le pedimos al menu que dibuje lo que tenga que dibujar
            self.menu.draw(self.screen)
            ## flip actualiza la pantalla con lo que le hemos pedido que dibuje
            ## antes. El draw de antes no actualiza la pantalla dibuja algo en
            ## la Surface screen, esta instrucción manda la Surface screen a la
            ## pantalla, para que se muestre en el monitor
            pygame.display.flip()

## Esperamos que eventualmente alguien le de enter a Start y pueda comenzar el
## juego, al dar enter en Start se debe ejecutar game.py:Game:__init__, ve al
## archivo game.py para continuar
