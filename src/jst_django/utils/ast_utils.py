import ast

import astor


def add_router_registration_with_import(source_code, view_class, basename, import_module=".views"):
    """
    Django routerga yangi view qo'shish va import qilish uchun AST funksiyasi.

    :param source_code: original python kodi (string)
    :param view_class: qo'shiladigan view class nomi (string)
    :param basename: router.register uchun basename (string)
    :param import_module: view qayerdan import qilinadi
    :return: yangilangan python kodi (string)
    """
    tree = ast.parse(source_code)

    # 1. Import qo'shish
    # oldin shunday import bor-yo'qligini tekshirish
    already_imported = False
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            if node.module == import_module:
                for n in node.names:
                    if n.name == view_class:
                        already_imported = True
                        break
    if not already_imported:
        import_node = ast.ImportFrom(module=import_module, names=[ast.alias(name=view_class, asname=None)], level=0)
        # odatda import fayl boshida bo‘ladi
        tree.body.insert(0, import_node)

    # 2. router.register chaqiruvini yaratish
    new_call = ast.Expr(
        value=ast.Call(
            func=ast.Attribute(value=ast.Name(id="router", ctx=ast.Load()), attr="register", ctx=ast.Load()),
            args=[ast.Constant(value=basename), ast.Name(id=view_class, ctx=ast.Load())],
            keywords=[ast.keyword(arg="basename", value=ast.Constant(value=basename))],
        )
    )

    # router assign keyin qo'shish
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if getattr(node.targets[0], "id", None) == "router":
                idx = tree.body.index(node)
                tree.body.insert(idx + 1, new_call)
                break

    return astor.to_source(tree)


def add_include_urlpattern(source_code, prefix, app_module):
    """
    urlpatterns ga yangi include qo'shadi:
        path("prefix/", include("app_module"))

    :param source_code: original python kodi (string)
    :param prefix: url prefix, masalan "accounts/"
    :param app_module: app modul nomi, masalan "accounts.urls"
    :return: yangilangan python kodi (string)
    """
    tree = ast.parse(source_code)

    # include chaqiruvini yaratish
    include_call = ast.Call(
        func=ast.Name(id="include", ctx=ast.Load()), args=[ast.Constant(value=app_module)], keywords=[]
    )

    # path chaqiruvini yaratish
    path_call = ast.Call(
        func=ast.Name(id="path", ctx=ast.Load()), args=[ast.Constant(value=prefix), include_call], keywords=[]
    )

    # urlpatterns ni topib list oxiriga qo'shish
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if getattr(node.targets[0], "id", None) == "urlpatterns":
                if isinstance(node.value, ast.List):
                    node.value.elts.append(path_call)
                    break

    return astor.to_source(tree)


def add_module(source_code, module) -> str:
    """
    appni MODULES ga qo'shadi

    :param source_code: python code
    :param module: qo'shilish kerak bo'lgan app
    :return: yangi code
    """
    tree = ast.parse(source_code)

    for node in tree.body:
        if isinstance(node, ast.Assign):
            if getattr(node.targets[0], "id", None) == "MODULES":
                if isinstance(node.value, ast.List):
                    node.value.elts.append(ast.Constant(value=module))
                    break
    return astor.to_source(tree)
