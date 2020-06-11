# Generated by Django 3.0.6 on 2020-06-11 23:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Город')),
            ],
            options={
                'verbose_name': 'Город',
                'verbose_name_plural': 'Города',
            },
        ),
        migrations.CreateModel(
            name='CloseReason',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Причина закрытия')),
            ],
            options={
                'verbose_name': 'Причина закрытия',
            },
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=280)),
                ('is_service', models.BooleanField()),
                ('is_used', models.BooleanField()),
                ('pub_date', models.DateField(auto_now_add=True, verbose_name='Дата публикации')),
                ('is_private', models.BooleanField(verbose_name='Приватное/общедоступное предложение')),
                ('moderation_statuses', models.CharField(choices=[('ON_MODERATION', 'На модерации'), ('APPROVED', 'Одобрено'), ('REFUSED', 'Отклонено')], default='ON_MODERATION', max_length=50, verbose_name='Статус модерации')),
                ('is_closed', models.BooleanField(verbose_name='Открытое/закрытое предложение')),
            ],
            options={
                'verbose_name': 'Предложение',
                'verbose_name_plural': 'Предложения',
            },
        ),
        migrations.CreateModel(
            name='OfferCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Наименование')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Регион')),
            ],
            options={
                'verbose_name': 'Регион',
                'verbose_name_plural': 'Регионы',
            },
        ),
        migrations.CreateModel(
            name='OfferPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.ImageField(blank=True, null=True, upload_to='offers/')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photo', to='offers.Offer')),
            ],
            options={
                'verbose_name': 'Фотография предложения',
                'verbose_name_plural': 'Фотографии предложения',
            },
        ),
    ]
