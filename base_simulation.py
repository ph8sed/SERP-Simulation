import pygame
import pandas as pd
import math
import sys
import os

CATALOG_PATH = "hipparcos-voidmain.csv"

WIDTH = 0
HEIGHT = 0


SHOW_STAR_NAMES = True
TARGET_STARS = 5
SHOW_INFO_PANEL = True

CONDITION_SETTINGS = {

    1:
    {
        "name": "Low Density - Low Color Variability",
        "limiting_mag": 4.5,
        "sky_color":
        (20,25,50),
        "visibility": 0.45,
        "color_variability": 0.01
    },


    2:
    {
        "name": "High Density - Low Color Variability",
        "limiting_mag": 7.0,
        "sky_color":
        (
            10,
            15,
            35
        ),

        "visibility": 0.85,

        "color_variability": 0.01
    },


    3:
    {
        "name": "Low Density - High Color Variability",

        "limiting_mag": 4.5,

        "sky_color":
        (
            20,
            25,
            50
        ),

        "visibility": 0.45,

        "color_variability": 1.0
    },


    4:
    {
        "name": "High Density - High Color Variability",

        "limiting_mag": 7.0,

        "sky_color":
        (
            5,
            10,
            30
        ),

        "visibility": 1.0,

        "color_variability": 1.0
    }

}

# below is the star database for the major stars

STAR_DATA = {


32349:
{
"name":"Sirius",

"constellation":
"Canis Major",

"distance":
"8.6 light years",

"type":
"A1V main sequence star",

"description":
"The brightest star in Earth's night sky."
},



27989:
{
"name":"Betelgeuse",

"constellation":
"Orion",

"distance":
"642 light years",

"type":
"Red supergiant",

"description":
"A massive red star nearing the end of its life."
},



24436:
{
"name":"Rigel",

"constellation":
"Orion",

"distance":
"860 light years",

"type":
"Blue supergiant",

"description":
"One of the brightest stars visible from Earth."
},



11767:
{
"name":"Polaris",

"constellation":
"Ursa Minor",

"distance":
"433 light years",

"type":
"Yellow supergiant",

"description":
"The North Star, located near the celestial pole."
},



91262:
{
"name":"Vega",

"constellation":
"Lyra",

"distance":
"25 light years",

"type":
"A0V main sequence star",

"description":
"One of the brightest stars in the northern sky."
},



91237:
{
"name":"Deneb",

"constellation":
"Cygnus",

"distance":
"2,600 light years",

"type":
"Blue-white supergiant",

"description":
"A major star in the Summer Triangle."
},



97649:
{
"name":"Altair",

"constellation":
"Aquila",

"distance":
"16.7 light years",

"type":
"A7V main sequence star",

"description":
"Rapidly rotating star in the Summer Triangle."
},



71683:
{
"name":"Antares",

"constellation":
"Scorpius",

"distance":
"550 light years",

"type":
"Red supergiant",

"description":
"The heart of the Scorpion constellation."
},



69673:
{
"name":"Arcturus",

"constellation":
"Boötes",

"distance":
"36.7 light years",

"type":
"K giant star",

"description":
"The brightest star in the northern celestial hemisphere."
},



80763:
{
"name":"Spica",

"constellation":
"Virgo",

"distance":
"250 light years",

"type":
"Blue giant binary",

"description":
"A bright close binary star system."
},



36850:
{
"name":"Procyon",

"constellation":
"Canis Minor",

"distance":
"11.5 light years",

"type":
"F5 main sequence star",

"description":
"One of the closest bright stars."
}


}

# drawing the stars

def magnitude_to_radius(mag):

    return max(
        1,
        min(
            6,
            int(
                (7-mag)/1.4
            )
        )
    )
def spectral_to_color(sp_type, variability):

    colors = {

        "O": (150, 180, 255),
        "B": (170, 200, 255),
        "A": (210, 220, 255),
        "F": (245, 240, 210),
        "G": (255, 230, 170),
        "K": (255, 190, 120),
        "M": (255, 140, 100)

    }


    if isinstance(sp_type, str):

        spectral_class = sp_type.strip()[0].upper()

        base = colors.get(
            spectral_class,
            (230,230,230)
        )

    else:

        base = (
            230,
            230,
            230
        )


    neutral = (
        230,
        230,
        230
    )


    return (

        int(neutral[0] * (1 - variability) + base[0] * variability),

        int(neutral[1] * (1 - variability) + base[1] * variability),

        int(neutral[2] * (1 - variability) + base[2] * variability)

    )


def magnitude_to_color(
        mag,
        visibility
):

    brightness = int(

        255 /
        (
            1 +
            max(
                mag,
                0
            )
            *
            0.15
        )

    )


    brightness = int(
        brightness *
        visibility
    )


    brightness = max(
        25,
        min(
            255,
            brightness
        )
    )


    return (
        brightness,
        brightness,
        min(
            255,
            brightness+20
        )
    )



def draw_star(
        surface,
        x,
        y,
        radius,
        color
):

    pygame.draw.circle(

        surface,

        color,

        (
            x,
            y
        ),

        radius

    )



    if radius >= 3:

        glow = pygame.Surface(
            (
                radius*8,
                radius*8
            ),
            pygame.SRCALPHA
        )


        pygame.draw.circle(

            glow,

            (
                min(255, color[0] + 30),
                min(255, color[1] + 30),
                min(255, color[2] + 30),
                80
            ),

            (
                radius*4,
                radius*4
            ),

            radius*3

        )


        surface.blit(

            glow,

            (
                x-radius*4,
                y-radius*4
            )

        )



# projection stuff

def sky_projection(
        ra,
        dec,
        view_ra,
        view_dec,
        zoom
):

    ra = math.radians(ra)
    dec = math.radians(dec)

    view_ra = math.radians(view_ra)
    view_dec = math.radians(view_dec)


    dra = ra-view_ra


    x = (
        math.cos(dec)
        *
        math.sin(dra)
    )


    y = (
        math.sin(dec)
        *
        math.cos(view_dec)

        -

        math.cos(dec)
        *
        math.sin(view_dec)
        *
        math.cos(dra)
    )


    z = (

        math.sin(dec)
        *
        math.sin(view_dec)

        +

        math.cos(dec)
        *
        math.cos(view_dec)
        *
        math.cos(dra)

    )


    if z <= 0:

        return None



    return (

        int(
            WIDTH/2
            -
            (x/z)*zoom
        ),

        int(
            HEIGHT/2
            -
            (y/z)*zoom
        )

    )

# background sky stuff

def draw_sky_background(
        screen,
        sky_color=None
):

    for y in range(HEIGHT):

        factor = y / HEIGHT


        # black at top, deep blue at bottom
        color = (

            int(2 + factor * 8),

            int(5 + factor * 12),

            int(15 + factor * 45)

        )


        pygame.draw.line(

            screen,

            color,

            (
                0,
                y
            ),

            (
                WIDTH,
                y
            )

        )


# loading the hipparcos dataset

def load_stars(
        limiting_mag
):


    if getattr(
            sys,
            "frozen",
            False
    ):

        path = os.path.join(
            sys._MEIPASS,
            CATALOG_PATH
        )

    else:

        path = CATALOG_PATH

    raw = pd.read_csv(
        path,
        header=None,
        low_memory=False
    )

    has_spectral = len(raw.columns) > 10

    if has_spectral:

        stars = raw.iloc[:, [1, 5, 8, 9, 76]]

        stars.columns = [
            "hip",
            "mag",
            "ra",
            "dec",
            "sp_type"
        ]

    else:

        stars = raw.iloc[:, [1, 5, 8, 9]]

        stars.columns = [
            "hip",
            "mag",
            "ra",
            "dec"
        ]

        stars["sp_type"] = None

    # Convert only numerical columns

    for column in [
        "hip",
        "mag",
        "ra",
        "dec"
    ]:
        stars[column] = pd.to_numeric(

            stars[column],

            errors="coerce"

        )

    # Remove rows missing numerical data only

    stars = stars.dropna(
        subset=[
            "hip",
            "mag",
            "ra",
            "dec"
        ]
    )



    stars = stars[

        stars["mag"]

        <=

        limiting_mag

    ]


    return stars


# blitting the info panel


def draw_information_panel(
        screen,
        font,
        info
):


    panel = pygame.Surface(
        (
            430,
            240
        ),
        pygame.SRCALPHA
    )


    panel.fill(
        (
            10,
            10,
            30,
            230
        )
    )


    lines = [

        info["name"],

        "",

        "Constellation: "
        +
        info["constellation"],

        "Distance: "
        +
        info["distance"],

        "Type: "
        +
        info["type"],

        "",

        info["description"]

    ]



    y = 15


    for line in lines:


        text = font.render(

            line,

            True,

            (
                220,
                230,
                255
            )

        )


        panel.blit(

            text,

            (
                15,
                y
            )

        )


        y += 25



    screen.blit(

        panel,

        (
            20,
            20
        )

    )


# viewer setup

def run_starmap(condition_id):

    condition = CONDITION_SETTINGS[condition_id]

    pygame.init()

    global WIDTH, HEIGHT

    info = pygame.display.Info()

    WIDTH = info.current_w
    HEIGHT = info.current_h

    screen = pygame.display.set_mode(
        (0,0),
        pygame.FULLSCREEN
    )


    pygame.display.set_caption(

        condition["name"]

    )


    font = pygame.font.SysFont(

        "Arial",

        18

    )



    stars = load_stars(

        condition["limiting_mag"]

    )


    print(

        condition["name"]

    )


    print(

        "Stars loaded:",

        len(stars)

    )




    star_database = []


    for _, star in stars.iterrows():


        hip = int(
            star["hip"]
        )

        star_database.append(

            {

                "ra":
                    star["ra"],

                "dec":
                    star["dec"],

                "mag":
                    star["mag"],

                "sp_type":
                    star["sp_type"],

                "radius":
                    magnitude_to_radius(
                        star["mag"]
                    ),

                "color":
                    tuple(
                        int(c * min(1, condition["visibility"] + 0.3))
                        for c in spectral_to_color(
                            star["sp_type"],
                            condition["color_variability"]
                        )
                    ),

                "info":
                    STAR_DATA.get(
                        hip
                    )

            }

        )



    # Camera

    view_ra = 0

    view_dec = 0


    zoom = 600



    selected_star = None
    clicked_stars = set()

    objective_complete = False


    clock = pygame.time.Clock()


    running = True



    while running:



        visible_click_targets = []



        for event in pygame.event.get():



            if event.type == pygame.QUIT:

                running = False



            if event.type == pygame.KEYDOWN:


                if event.key == pygame.K_ESCAPE:

                    running = False



            if event.type == pygame.MOUSEWHEEL:


                zoom += event.y * 50


                zoom = max(

                    150,

                    min(

                        2500,

                        zoom

                    )

                )

        # camera controls


        keys = pygame.key.get_pressed()



        if keys[pygame.K_LEFT]:

            view_ra += 0.5



        if keys[pygame.K_RIGHT]:

            view_ra -= 0.5



        if keys[pygame.K_UP]:

            view_dec += 0.5



        if keys[pygame.K_DOWN]:

            view_dec -= 0.5



        view_dec = max(

            -90,

            min(

                90,

                view_dec

            )

        )



        draw_sky_background(

            screen,

            condition["sky_color"]

        )



        # drawing the stars using pygame


        for star in star_database:



            pos = sky_projection(

                star["ra"],

                star["dec"],

                view_ra,

                view_dec,

                zoom

            )


            if pos is None:

                continue



            x,y = pos



            if (

                0 <= x < WIDTH

                and

                0 <= y < HEIGHT

            ):


                draw_star(

                    screen,

                    x,

                    y,

                    star["radius"],

                    star["color"]

                )



                # store clickable stars

                if star["info"]:


                    visible_click_targets.append(

                        {

                        "x":x,

                        "y":y,

                        "info":
                        star["info"]

                        }

                    )



                    if SHOW_STAR_NAMES:


                        label = font.render(

                            star["info"]["name"],

                            True,

                            (

                                180,

                                200,

                                255

                            )

                        )


                        screen.blit(

                            label,

                            (

                                x+8,

                                y-10

                            )

                        )

        if selected_star and SHOW_INFO_PANEL:
            draw_information_panel(
                screen,
                font,
                selected_star
            )

        # clicking on stars

        if pygame.mouse.get_pressed()[0]:

            mx, my = pygame.mouse.get_pos()

            for target in visible_click_targets:

                distance = math.sqrt(
                    (mx - target["x"]) ** 2
                    +
                    (my - target["y"]) ** 2
                )

                if distance < 30:

                    selected_star = target["info"]

                    # Add star to discovered list
                    if selected_star:

                        clicked_stars.add(
                            selected_star["name"]
                        )

                        if len(clicked_stars) >= TARGET_STARS:
                            objective_complete = True


        # objective ui

        if objective_complete:

            objective_text = font.render(
                "Objective Complete: 5 major stars identified. "
                "Continue exploring for the remainder of time.",
                True,
                (
                    80,
                    255,
                    120
                )
            )

        else:

            objective_text = font.render(
                f"Identify major stars: {len(clicked_stars)}/{TARGET_STARS}",
                True,
                (
                    220,
                    220,
                    255
                )
            )

        screen.blit(
            objective_text,
            (
                20,
                HEIGHT - 40
            )
        )
        pygame.display.flip()


        clock.tick(60)



    pygame.quit()
