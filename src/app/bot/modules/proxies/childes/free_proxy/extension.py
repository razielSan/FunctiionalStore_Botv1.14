from fp.fp import FreeProxy


def get_free_proxy(
    https,
    rand,
    anonym,
    elite,
):
    return FreeProxy(
        https=https,
        rand=rand,
        anonym=anonym,
        elite=elite,
    )
