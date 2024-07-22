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
            'name': 'Post instagram',
            'pixel_size': '1200x1200',
            'delivery_format': '.png'
        },
        {
            'name': 'Arte WhatsApp',
            'pixel_size': '1200x1200',
            'delivery_format': '.png'
        },
        {
            'name': ' Flyer Digital',
            'pixel_size': '425x595',
            'delivery_format': '.png e .jpeg'
        },
        {
            'name': 'Cartão visita digital',
            'pixel_size': '1200x1200',
            'delivery_format': '.png'
        },
        {
            'name': 'Assinatura de e-mail',
            'pixel_size': '70x400',
            'delivery_format': '.png'
        },
        {
            'name': 'Convite digital',
            'pixel_size': '1200x800',
            'delivery_format': '.png'
        },
        {
            'name': 'Banner para site',
            'pixel_size': 'personalizado',
            'delivery_format': '.png'
        },
        {
            'name': 'Anúncios IG e FB',
            'pixel_size': '1200x1200',
            'delivery_format': '.png'
        }
    ]

    for spec_data in specifications:
        Specification.objects.create(**spec_data)


if __name__ == '__main__':
    create_packages()
    create_specifications()
    print('Data populated!')