from aiogram import types
from asyncio import sleep
from random import choice, randint


async def make_Naya_happy_again(message: types.Message):
    wait = 1
    img = _get_heart_stickers()
    bot_message = await message.answer('.')
    # bot_message = await message.answer('<b>Пора бы запомнить, что я тебя люблю, сладкая 😘 </b>', parse_mode="HTML")
    # emojis = ["🙎‍♀️", "👩‍❤️‍💋‍👨", "💍", "👰‍♀️" , "🤵", "💒", "🤰", "🤱",  "👨‍👩‍👦", "👨‍👩‍👧‍👦"]
    # await sleep(2)
    # for e in emojis:
    #     await bot_message.edit_text(e)
    #     await sleep(wait)
    for anim in img:
        await bot_message.edit_text('\n'.join(anim))
        await sleep(0.5)


def _get_heart_stickers():
    return (
        (
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',
            '🖤🖤🖤🖤❤🖤🖤🖤🖤',
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',

        ),
        (
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',
            '🖤🖤🖤❤❤❤🖤🖤🖤',
            '🖤🖤🖤🖤❤🖤🖤🖤🖤',
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',
        ),
        (
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',
            '🖤🖤❤❤🖤❤❤🖤🖤',
            '🖤🖤❤❤❤❤❤🖤🖤',
            '🖤🖤🖤❤❤❤🖤🖤🖤',
            '🖤🖤🖤🖤❤🖤🖤🖤🖤',
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',
        ),
        (
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',
            '🖤🖤❤❤🖤❤❤🖤🖤',
            '🖤❤❤❤❤❤❤❤🖤',
            '🖤❤❤❤❤❤❤❤🖤',
            '🖤🖤❤❤❤❤❤🖤🖤',
            '🖤🖤🖤❤❤❤🖤🖤🖤',
            '🖤🖤🖤🖤❤🖤🖤🖤🖤',
            '🖤🖤🖤🖤🖤🖤🖤🖤🖤',
        ),
        (
            '🖤❤❤❤🖤❤❤❤🖤',
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
            '🖤❤❤❤❤❤❤❤🖤',
            '🖤🖤❤❤❤❤❤🖤🖤',
            '🖤🖤🖤❤❤❤🖤🖤🖤',
            '🖤🖤🖤🖤❤🖤🖤🖤🖤',
        ),
        (
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
            '🖤❤❤❤❤❤❤❤🖤',
            '🖤🖤❤❤❤❤❤🖤🖤',
            '🖤🖤🖤❤❤❤🖤🖤🖤',
        ),
        (
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤❤🤍❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
        ),
        (
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤🤍🤍🤍❤❤❤',
            '❤❤❤❤🤍❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
        ),
        (
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
            '❤❤🤍🤍❤🤍🤍❤❤',
            '❤❤🤍🤍🤍🤍🤍❤❤',
            '❤❤❤🤍🤍🤍❤❤❤',
            '❤❤❤❤🤍❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
        ),
        (
            '❤❤❤❤❤❤❤❤❤',
            '❤❤🤍🤍❤🤍🤍❤❤',
            '❤🤍🤍🤍🤍🤍🤍🤍❤',
            '❤🤍🤍🤍🤍🤍🤍🤍❤',
            '❤❤🤍🤍🤍🤍🤍❤❤',
            '❤❤❤🤍🤍🤍❤❤❤',
            '❤❤❤❤🤍❤❤❤❤',
            '❤❤❤❤❤❤❤❤❤',
        )
    )

async def make_Naya_happy(message: types.Message):
    words = (
        'удивительная', 'внимательная', 'красивая', 'лучшая', 'успешная', 'заботливая', 'милая', 'прекрасная',
        'умная', 'шикарная', 'обалденная', 'очаровашка', 'любимая', 'весёлая', 'нежная', 'яркая', 'прелестная',
        'приятная', 'сладкая', 'дивная', 'ангельская', 'добрая', 'бесподобная', 'волшебная', 'крутышка', 'смелая',
        'ласковая', 'романтичная', 'великолепная', 'внимательная', 'страстная', 'игривая', 'единственная',
        'стройная', 'безумная', 'симпатичная', 'изящная', 'талантливая', 'элегантная', 'чуткая', 'уникальная',
    )
    await __rabbit(message)
    bot_message = await message.answer('<b>Крошечные напоминания того, что ты...</b>', parse_mode="HTML")
    await sleep(2)

    for word in words:
        await bot_message.edit_text(f'<b>Cамая {word}✨</b>', parse_mode="HTML")
        await sleep(0.5)

    await bot_message.edit_text(f'<b> Ная = the best🤗</b>', parse_mode="HTML")


async def __rabbit(message: types.Message):
    left_eyes = '┈┃▋▏▋▏┃┈'
    right_eyes = '┈┃╱▋╱▋┃┈'
    img = [
        '╭━━╮╭━━╮',
        '╰━╮┃┃╭━╯',
        '┈╭┛┗┛┗╮┈',
        '┈┃╱▋╱▋┃┈',
        '╭┛▔▃▔┈┗╮',
        '╰┓╰┻━╯┏╯',
        '╭┛┈┏┓┈┗╮',
        '╰━━╯╰━━╯',
    ]
    eyes = choice((True, False))
    img[3] = right_eyes if eyes else left_eyes
    bot_message = await play_stroke_anim(message, img)
    await sleep(1)

    for _ in range(randint(5, 10)):
        eyes = not eyes
        img[3] = right_eyes if eyes else left_eyes
        await bot_message.edit_text('\n'.join(img))
        await sleep(0.5)


async def play_stroke_anim(msg: types.Message, anims, tick=0.1):
    bot_message = await msg.answer("Привет!")
    for i in range(len(anims)):
        data = "\n".join(anims[0:i + 1])
        await bot_message.edit_text(data)
        await sleep(tick)
    return bot_message