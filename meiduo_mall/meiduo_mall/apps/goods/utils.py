



# 获取面包屑导航：参数category是分类类别对象，可能是一级，二级，三级，返回包括本身的迭代父级类别
def get_breadcrumb(category):
    breadcrumb = {
        'cat1': '',
        'cat2': '',
        'cat3': '',
    }

    if category.parent == None:
        # 没有父级，说明是一级类别
        breadcrumb['cat1'] = category
    elif category.subs.count() == 0:
        # 没有子级，说明为三级类别
        breadcrumb['cat3'] = category
        breadcrumb['cat2'] = category.parent
        breadcrumb['cat1'] = category.parent.parent
    else:
        # 二级类别
        breadcrumb['cat2'] = category
        breadcrumb['cat1'] = category.parent

    return breadcrumb
























































