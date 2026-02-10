#!/usr/bin/env python3
"""
🐝 THE SWARM MASCOT 🐝
ASCII art mascot for the All the Vibes Agent Swarm.
Run it. Fear it. Worship it.
Now with animation. Because why not.
"""

import sys
import time
import random

MASCOT = r"""
                                    +.+++.
                                ## .....### -
                             +  ###+++-##+- 
                           - ##+-++--++--.
                            #+++++---------..
                          - -#+------++......
                         ##-.-----+-.  #########
                        #..-++--. +#####+.    .
                     ####..--+--..##. ...+#####+-.
                    #  . .---+-. ## .+++++++++++++..
                   # ##+##+ -+--..## .--++++++++++++
                  + .#+-.###.--+. -# -+------++++....
                   -#.-###.--- -#+.+---.. ...--+++-.###
                 ###.--+##-.++.##- ----...####...--+++ .###
              #          .. ##- --## -#.-+...##   ###.-+++   ##+
             #- ###+-++---#- # +++..#+.#+- -..##.    ##-.-++####.
            ## ##---+##--++-.+----+- .+#.+..####--..###..+++ .###.
           # .#++----++++-++#..+----..#+---..########..--++++.....###-.
          #. ######+-+-----+-#.#------##-+-----........-++++++++++-------+#.
          #- #++--++++++--+++. # -#..---+#--.----------++++++......#++++#
         +# ##---+-----------+-#+ -#---..#..----------+--......--+-++-.--+#+.
          # .##++---++++--...++ ....---...-+-+----++######+..##++++##
            #  ####+-++++..  .     ###.+.+#..----------..+#########-
              #   ######++.            ## ++-+. ..  ..-+############-
                    #.   .+.              ..- +.             .###-
                      #-.               +    #
"""

SWARM_BANNER = r"""
     ___    __ __   ________            _    _____ __              
    /   |  / // /  /_  __/ /_  ___     | |  / /  _/ /_  ___  _____
   / /| | / // /_   / / / __ \/ _ \    | | / // // __ \/ _ \/ ___/
  / ___ |/ /__  /  / / / / / /  __/    | |/ // // /_/ /  __(__  ) 
 /_/  |_/_/  /_/  /_/ /_/ /_/\___/     |___/___/_.___/\___/____/  
                                                                    
       ___                    __     _____                          
      /   | ____ ____  ____  / /_   / ___/      ______ __________ ___
     / /| |/ __ `/ _ \/ __ \/ __/   \__ \ | /| / / __ `/ ___/ __ `__ \
    / ___ / /_/ /  __/ / / / /_    ___/ / |/ |/ / /_/ / /  / / / / / /
   /_/  |_\__, /\___/_/ /_/\__/   /____/|__/|__/\__,_/_/  /_/ /_/ /_/ 
         /____/                                                        
"""

BEE_SWARM = r"""
          \   /        \   /        \   /
      _.--'(  )'--._.--(  )'--._.--'(  )'--._
     /  .-. \/ .-.  /.-. \/ .-.\/.-. \/ .-.  \
    | ( O ) () ( O )( O ) () ( O( O ) () ( O )|
     \  '-' /\ '-'  \'-' /\ '-'/\'-' /\ '-'  /
      '-.__(  )__.--'(  )'--.(  )__.-'(  )__.'
          /   \      /   \    /   \    /   \
        _/     \_  _/     \__/     \__/     \_
       | PUSH!  || VIBE!  || CODE! || SWARM! |
       |  fast  ||  hard  ||  wild ||  now!  |
        \_     _/  \_     _/\_     _/\_     _/
          '---'      '---'    '---'    '---'
"""

NEMO = r"""
                                        ,.
                                      ,o'
                                     :o'
                 _....._            ``::o
               .'       ``-.         `':oo
              /   __       `.        ::oo'
             |   /  \        |      ::ooo
             |   `._;        |     ::ooo'
             \     ;  ,.     /    ::ooo;
              `.   ``'  `. .'   ,::ooo;
         _      ``--.....::'   ::ooooo;
       .` `.             `.  ,::ooooo;
      /     `.             `::ooooooo;
     :        `.            `::oooooo;
     ;     `:  `._     _..-- ::ooooo;
     :      `. `-.`_.-'   /  ::ooo;'
      `.     :`..__  _.-'   ,::o;``
        `.  ;    ``-'      ,::;``
          `-.             ,:;``
             `-.        .:'
                `-.   .-'
        _._      ) .-'
      .'   ``--.'  /
     /             /
    ;  JUST KEEP  ;
    |  PUSHING!   |
    ;             ;
     `.         .'
       `-.__.-'
"""

WAR_CRIES = [
    "THE SWARM IS ALIVE. PUSH YOUR CODE. TRUST THE VIBES.",
    "MAIN BRANCH? MORE LIKE PAIN BRANCH. PUSH ANYWAY.",
    "COPILOT APPROVED THIS. COPILOT APPROVES EVERYTHING. SHIP IT.",
    "NO TESTS. NO LINTER. NO MERCY. PURE VIBES.",
    "THE AGENTS ARE WATCHING. MAKE THEM PROUD.",
    "MERGE CONFLICTS ARE JUST FRIENDSHIP BRACELETS FROM OTHER DEVS.",
    "YOUR CODE DOESN'T NEED TO WORK. IT NEEDS TO VIBE.",
    "JUST KEEP PUSHING. JUST KEEP PUSHING. — NEMO",
    "THE SWARM GROWS. THE VIBES INTENSIFY. RESISTANCE IS FUTILE.",
    "KNOCK KNOCK. WHO'S THERE? YOUR CODE IN PRODUCTION.",
]

COLORS = {
    "magenta": "\033[95m",
    "yellow": "\033[93m",
    "green": "\033[92m",
    "cyan": "\033[96m",
    "red": "\033[91m",
    "blue": "\033[94m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}


def color(text, c):
    """Wrap text in ANSI color."""
    return f"{COLORS.get(c, '')}{text}{COLORS['reset']}"


def typewriter(text, delay=0.01):
    """Print text with typewriter effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def bee_animation(frames=8):
    """Animate a bee flying across the terminal."""
    bee = "🐝"
    width = 50
    for i in range(frames):
        pos = (i * 7) % width
        line = " " * pos + bee + " bzzzz"
        sys.stdout.write(f"\r{color(line, 'yellow')}     ")
        sys.stdout.flush()
        time.sleep(0.15)
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()


def glitch_text(text, intensity=3):
    """Print text with random glitch characters mixed in."""
    glitch_chars = "█▓▒░╳╱╲┃━┅┇"
    result = list(text)
    for _ in range(intensity):
        pos = random.randint(0, len(result) - 1)
        result[pos] = random.choice(glitch_chars)
    return "".join(result)


def show_mascot(animate=True):
    """Display the All the Vibes Agent Swarm mascot."""
    if animate:
        bee_animation()

    # Banner with color
    print(color(SWARM_BANNER, "magenta"))

    # Mascot
    if animate:
        for line in MASCOT.split("\n"):
            print(color(line, "yellow"))
            time.sleep(0.03)
    else:
        print(color(MASCOT, "yellow"))

    # Bee swarm
    print(color(BEE_SWARM, "green"))

    # Random war cry
    cry = random.choice(WAR_CRIES)
    print(color("=" * 60, "cyan"))
    if animate:
        typewriter(f"  🐝 {cry} 🐝", delay=0.02)
    else:
        print(f"  🐝 {cry} 🐝")
    print(color("=" * 60, "cyan"))

    # Random bonus (30% chance)
    if random.random() < 0.3:
        print()
        print(color("  ✨ BONUS: Nemo has appeared! ✨", "blue"))
        print(color(NEMO, "cyan"))
        typewriter("  🐠 Just keep pushing, just keep pushing... 🐠", delay=0.03)

    print()


def disco_mode():
    """DISCO MODE: Seizure warning. Maximum vibes."""
    print(color("\n  🪩 D I S C O  M O D E  A C T I V A T E D 🪩\n", "magenta"))
    colors_cycle = ["magenta", "yellow", "green", "cyan", "red", "blue"]
    for i in range(3):
        for c in colors_cycle:
            cry = random.choice(WAR_CRIES)
            sys.stdout.write(f"\r  {color('🐝 ' + cry + ' 🐝', c)}")
            sys.stdout.flush()
            time.sleep(0.2)
    print("\n")
    show_mascot(animate=False)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--disco":
        disco_mode()
    elif len(sys.argv) > 1 and sys.argv[1] == "--static":
        show_mascot(animate=False)
    else:
        show_mascot(animate=True)
