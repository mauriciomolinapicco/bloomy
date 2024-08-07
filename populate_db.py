from bloomy.models import Package, Specification

def create_packages():
    packages = [
        {
            'name': 'Pacote 1',
            'allowed_usages': 10,
            'price': 1000,
            'stripe_product_id': 'price_1PYRuERwrwuuCK4afvgJ4te3',
        },
        {
            'name': 'Pacote 2',
            'allowed_usages': 20,
            'price': 1800,
            'stripe_product_id': 'price_1PYS75RwrwuuCK4aM9ejFn4W',
        }, 
        {
            'name': 'Pacote 3',
            'allowed_usages': 30,
            'price': 2400,
            'stripe_product_id': 'price_1PYS82RwrwuuCK4aESpT2ToB',
        }
    ]

    for package_data in packages:
        Package.objects.create(**package_data)


def create_specifications():
    specifications = [
        {
            'name': 'Post para redes sociais (1080x1080px)',
        },
        {
            'name': 'Stories para instagram (1080x1920px)',
        },
        {
            'name': 'Capa de reels (1080x1920px)',
        },
        {
            'name': 'Banner para site (1920x700px)',
        },
        {
            'name': 'Arte para WhatsApp (1080x1080px)',
        },
        {
            'name': 'Flyer digital (10x15cm)',
        },
        {
            'name': 'Cartão de visita digital (1080x1920px)',
        },
        {
            'name': 'Timbrado digital (A4)',
        },
        {
            'name': 'Assinatura de e-mail (70x300px)',
        },
        {
            'name': 'Banner para LinkedIn (1200x627px)',
        },
        {
            'name': 'Convite digital (1080x1080px)',
        },
        {
            'name': 'Anúncia para redes sociais (1080x1080px ou 1080x1920px)',
        },
        {
            'name': 'Estampa de camiseta corporativa (20x20cm)',
        },
        {
            'name': 'Estampa de Ecobag corporativa (20x20cm)',
        },
        {
            'name': 'Arte para brinde corporativo',
        }
        
    ]

    for spec_data in specifications:
        Specification.objects.create(**spec_data)


if __name__ == '__main__':
    create_packages()
    create_specifications()
    print('Data populated!')