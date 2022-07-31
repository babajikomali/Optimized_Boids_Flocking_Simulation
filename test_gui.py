import pygame
import pygame_gui

SCREEN_WIDTH = 1380
SCREEN_HEIGHT = 620
STIMULATION_WDITH = 1000
STIMULATION_HEIGHT = 600
GUI_WIDTH = 350
GUI_HEIGHT = 600

pygame.init()

pygame.display.set_caption('Test Gui')
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), 
                                theme_path = 'theme.json',
                                enable_live_theme_updates = False,
                                )
background = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
background.fill(color='#21282D')

X = STIMULATION_WDITH + 20 ; Y = 10
SPACING = 10

title = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((X+10, Y), (GUI_WIDTH, 30)),
                                        text='Flock Stimulation',
                                        manager=manager,
                                        anchors={'top': 'top',
                                                 'left': 'left',
                                                 'bottom': 'top',
                                                 'right': 'left'})
Y += 30
fps_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((X+10, Y), (-1, 30)),
                                        text='FPS :',
                                        manager=manager,
                                        anchors={'top': 'top',
                                                 'left': 'left',
                                                 'bottom': 'top',
                                                 'right': 'left'})
fps = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, Y), (-1, 30)),
                                        text='60',
                                        manager=manager,
                                        anchors={'top': 'top',
                                                 'left': 'left',
                                                 'bottom': 'top',
                                                 'right': 'left',
                                                 'left_target': fps_label})
num_boids_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((30, Y), (-1, 30)),
                                        text='Boids :',
                                        manager=manager,
                                        anchors={'top': 'top',
                                                 'left': 'left',
                                                 'bottom': 'top',
                                                 'right': 'left',
                                                 'left_target': fps})
num_boids = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, Y), (-1, 30)),
                                        text='100',
                                        manager=manager,
                                        anchors={'top': 'top',
                                                 'left': 'left',
                                                 'bottom': 'top',
                                                 'right': 'left',
                                                 'left_target': num_boids_label})


Y = 300
UI_INFORMATION_X = 1000
UI_INFORMATION_y = 10

stimulate = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((X, Y+5), (-1, 30)),
                                        text='Stimulate',
                                        manager=manager,
                                        anchors={'top': 'top',
                                                 'left': 'left',
                                                 'bottom': 'top',
                                                 'right': 'left'})
reset = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, Y+5), (-1, 30)),
                                        text='Reset',
                                        manager=manager,
                                        anchors={'top': 'top',
                                                 'left': 'left',
                                                 'bottom': 'top',
                                                 'right': 'left',
                                                 'left_target': stimulate})
randomize = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, Y+5), (-1, 30)),
                                        text='Randomize',
                                        manager=manager,
                                        anchors={'top': 'top',
                                                 'left': 'left',
                                                 'bottom': 'top',
                                                 'right': 'left',
                                                 'left_target': reset})

ROW_SPACING = 10
Y = Y+50

alignment = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((X+5, Y), (-1, 30)),
                                        text='Alignment',
                                        manager=manager,
                                        anchors={'top': 'top',
                                                 'left': 'left',
                                                 'bottom': 'top',
                                                 'right': 'left'})
cohesion = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, Y), (-1, 30)),
                                        text='Cohesion',
                                        manager=manager,
                                        anchors={'top': 'top',
                                                 'left': 'left',
                                                 'bottom': 'top',
                                                 'right': 'left',
                                                 'left_target': alignment})
separation = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, Y), (-1, 30)),
                                        text='Separation',
                                        manager=manager,
                                        anchors={'top': 'top',
                                                 'left': 'left',
                                                 'bottom': 'top',
                                                 'right': 'left',
                                                 'left_target': cohesion})

# sliders
SLIDER_LENGTH = 230
label10 = pygame_gui.elements.UILabel(pygame.Rect((X, ROW_SPACING),(-1,25)),
                                    text='label 10',
                                    manager=manager,
                                    anchors={'top': 'top',
                                           'left': 'left',
                                           'bottom': 'top',
                                           'right': 'left',
                                           'top_target': alignment})
slider1 = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((5,ROW_SPACING),(SLIDER_LENGTH,25)),
                                        start_value=0,
                                        value_range=(0,5),
                                        click_increment=1,
                                        manager=manager,
                                        anchors={'top': 'top',
                                           'left': 'left',
                                           'bottom': 'top',
                                           'right': 'left',
                                           'top_target': alignment,
                                           'left_target': label10})
label11 = pygame_gui.elements.UILabel(pygame.Rect((5, ROW_SPACING),(-1,25)),
                                    text=str(int(slider1.get_current_value())),
                                    manager=manager,
                                    anchors={'top': 'top',
                                           'left': 'left',
                                           'bottom': 'top',
                                           'right': 'left',
                                           'top_target': alignment,
                                           'left_target': slider1})

# slider 2
label20 = pygame_gui.elements.UILabel(pygame.Rect((X, ROW_SPACING),(-1,25)),
                                    text='label 20',
                                    manager=manager,
                                    anchors={'top': 'top',
                                           'left': 'left',
                                           'bottom': 'top',
                                           'right': 'left',
                                           'top_target': label10})
slider2 = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((5,ROW_SPACING),(SLIDER_LENGTH,25)),
                                        start_value=0,
                                        value_range=(0,5),
                                        click_increment=1,
                                        manager=manager,
                                        anchors={'top': 'top',
                                           'left': 'left',
                                           'bottom': 'top',
                                           'right': 'left',
                                           'top_target': label10,
                                           'left_target': label20})
label21 = pygame_gui.elements.UILabel(pygame.Rect((5, ROW_SPACING),(-1,25)),
                                    text=str(int(slider1.get_current_value())),
                                    manager=manager,
                                    anchors={'top': 'top',
                                           'left': 'left',
                                           'bottom': 'top',
                                           'right': 'left',
                                           'top_target': label10,
                                           'left_target': slider2})

# slider 3
label30 = pygame_gui.elements.UILabel(pygame.Rect((X, ROW_SPACING),(-1,25)),
                                    text='label 20',
                                    manager=manager,
                                    anchors={'top': 'top',
                                           'left': 'left',
                                           'bottom': 'top',
                                           'right': 'left',
                                           'top_target': label20})
slider3 = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((5,ROW_SPACING),(SLIDER_LENGTH,25)),
                                        start_value=0,
                                        value_range=(0,5),
                                        click_increment=1,
                                        manager=manager,
                                        anchors={'top': 'top',
                                           'left': 'left',
                                           'bottom': 'top',
                                           'right': 'left',
                                           'top_target': label20,
                                           'left_target': label30})
label31 = pygame_gui.elements.UILabel(pygame.Rect((5, ROW_SPACING),(-1,25)),
                                    text=str(int(slider1.get_current_value())),
                                    manager=manager,
                                    anchors={'top': 'top',
                                           'left': 'left',
                                           'bottom': 'top',
                                           'right': 'left',
                                           'top_target': label20,
                                           'left_target': slider3})

stimulation_surface = pygame.Surface((STIMULATION_WDITH, STIMULATION_HEIGHT))
stimulation_surface.fill(color='#0A0A0A')

clock = pygame.time.Clock()
is_running = True

while is_running:
    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == stimulate : print('Stimulate button pressed.')
            if event.ui_element == reset : print('Reset button pressed')
            if event.ui_element == randomize : print('Randomize button pressed')


        manager.process_events(event)

    manager.update(time_delta)

    screen.blit(background, (0, 0))
    manager.draw_ui(screen)
    screen.blit(stimulation_surface,(10,10))

    pygame.display.update()