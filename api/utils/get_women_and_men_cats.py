from api.models import Category


def getWomenAndMenCats():
    '''
    @return `[menCats, womenCats]` tuple
    '''
    menCats = Category.objects.filter(
        level=1, gender='men').values_list('categoryId', flat=True)
    womenCats = Category.objects.filter(
        level=1, gender='women').values_list('categoryId', flat=True)
    menCats = [str(catId) for catId in menCats]
    womenCats = [str(catId) for catId in womenCats]
    return [menCats, womenCats]
