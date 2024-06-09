from wordcloud import WordCloud

thank_you_dict = {
    'Thank you': 100,
    'Gracias': 85,
    '谢谢': 98,
    'Danke': 75,
    'Merci': 80,
    'ありがとう': 70,
    'Спасибо': 90,
    'شكرا': 95,
    '감사합니다': 60,
    'Grazie': 78,
    'धन्यवाद': 88,
    'Obrigado': 77,
    'ευχαριστώ': 50,
    'ขอบคุณ': 65,
    'Mulțumesc': 40,
    'Dank u': 45,
    'Tack': 55,
    'Kiitos': 42,
    'Hvala': 38,
    'Dziękuję': 100,
    'Teşekkür ederim': 82,
    'Cảm ơn': 68,
    'Dankon': 35,
    'Mahadsanid': 30,
    'Shukriya': 59,
    'Terima kasih': 62,
    'Ačiū': 37,
    'Diolch': 34,
    'Takk': 44,
    'Salamat': 61,
    'Asante': 48,
    'Mersi': 36,
    'Köszönöm': 47,
    'Děkuji': 53,
    'Eskerrik asko': 31,
    'Multumesc': 40,
    'Gràcies': 57,
    'Mange tak': 43,
    'Paljon kiitoksia': 42,
    'Spasibo': 90,
    'Xie xie': 98,
    'Dankie': 41,
    'Chokran': 95,
    'Arigato': 70,
    'Kamsahamnida': 60,
}


def generate():
    wc = WordCloud(background_color='white')
    wc.generate_from_frequencies(thank_you_dict)

    svg_string = wc.to_svg()
    with open('./thank_you.svg', 'w', encoding='utf-8') as f:
        f.write(svg_string)


if __name__ == '__main__':
    generate()
