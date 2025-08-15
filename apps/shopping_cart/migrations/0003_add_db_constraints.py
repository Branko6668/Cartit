from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("shopping_cart", "0002_alter_shoppingcart_options_shoppingcart_selected_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE shopping_cart
                MODIFY COLUMN create_time DATETIME DEFAULT CURRENT_TIMESTAMP;
            """,
            reverse_sql="""
                ALTER TABLE shopping_cart
                MODIFY COLUMN create_time DATETIME;
            """
        ),
    ]
