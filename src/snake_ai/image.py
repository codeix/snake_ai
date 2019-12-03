from snake_ai.brain import Brain
from PIL import Image


def gen():

    brain = Brain([2, 100, 3])
    brain.random(60)

    img = Image.new('RGB', (100, 300))
    pixels = img.load()

    import pdb;pdb.set_trace()
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            func = lambda x: int(255*(x+1)/2)

            color = tuple(map(func, brain.apply((x, y))))
            pixels[x, y] = color
            r, g, b = color
            print('x=%s, y=%s r=%s g=%s b=%s' % (x,y, r, g, b))

    print(brain.apply((1, 2)))

    img.save('neuro_image.png')

