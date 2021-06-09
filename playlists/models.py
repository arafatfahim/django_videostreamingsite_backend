from django.db import models
from django.db.models import Avg, Max, Min
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models.signals import  pre_save
from django.utils import timezone
from django.utils.text import slugify
from djangoflix.db.models import PublishStateOptions
from djangoflix.db.receivers import publish_state_pre_save, slugify_pre_save
from videos.models import Video
from tags.models import TaggedItem
from categories.models import Category
from ratings.models import Rating

# Create your models here.
class PublishStateOptions(models.TextChoices):
        #CONSTANT = DB_VALUE, USER_DISPLAY_VA
        PUBLISH = 'PU', 'Publish'
        DRAFT = 'DR', 'Draft'
        #UNLISTED = 'UN', 'Unlisted'
        #PRIVATE = 'PR', 'Private'


class VideoQuerySet(models.QuerySet):
    def published(self):
        now = timezone.now()
        return self.filter(
            state=PublishStateOptions.PUBLISH, 
            publish_timestamp__lte= now
        )
class PlaylistManager(models.Manager):
    def get_queryset(self):
        return VideoQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()

    def fetured_playlists(self):
        return self.get_queryset().filter(type=Playlist.PlaylistTypeChoices.PLAYLIST)



class Playlist(models.Model):
    class PlaylistTypeChoices(models.TextChoices):
        #CONSTANT = DB_VALUE, USER_DISPLAY_VA
        MOVIE = 'MOV', 'Movie'
        SHOW = 'TVS', 'TV Show'
        SEASON = 'SEA', 'Season'
        PLAYLIST = 'PLY', 'Playlist'


    parent = models.ForeignKey("self", blank=True, on_delete=models.SET_NULL,null=True)
    order = models.IntegerField(default=1)
    category = models.ForeignKey(Category, related_name='playlists', blank=True, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=3, choices=PlaylistTypeChoices.choices, default=PlaylistTypeChoices.PLAYLIST)
    description =models.TextField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    video = models.ForeignKey(Video, related_name='playlist_featured', blank=True,
    null=True, on_delete=models.SET_NULL)
    videos = models.ManyToManyField(Video, related_name='playlist_item', blank=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    state = models.CharField(max_length=2, choices=PublishStateOptions.choices, 
    default=PublishStateOptions.DRAFT)
    publish_timestamp = models.DateTimeField(auto_now_add=False, auto_now=False,
    blank=True, null=True)
    tags = GenericRelation(TaggedItem, related_query_name='playlist')
    ratings = GenericRelation(Rating, related_query_name='playlist')
    
    objects = PlaylistManager()

    def __str__(self):
        return self.title

    def get_rating_avg(self):
        return Playlist.objects.filter(id=self.id).aggregate(Avg("rating_set_value"))

    def get_rating_spread(self):
        return Playlist.objects.filter(id=self.id).aggregate(max=Max("rating_set_value"), min=Min("rating_set_value"))

    @property
    def is_published(self):
        return self.active


class TVShowProxyManager(PlaylistManager):
    def all(self):
        return self.get_queryset().filter(parent__isnull=True, type=Playlist.PlaylistTypeChoices.SHOW)

class TVShowProxy(Playlist):

    objects = TVShowProxyManager()

    def __str__(self):
        return self.title
    class Meta:
        proxy = True
        verbose_name = 'TV Show'
        verbose_name_plural = 'TV Shows'

    def save(self, *args, **kwargs):
        self.type = Playlist.PlaylistTypeChoices.SHOW
        super().save(*args, **kwargs)

    @property
    def seasons(self):
        return self.playlist_set.published()

    def get_short_display(self):
        return f"{self.seasons.count()} Seasons"



class TVShowSeasonProxyManager(PlaylistManager):
    def all(self):
        return self.get_queryset().filter(parent__isnull=False, type=Playlist.PlaylistTypeChoices.SEASON)

class TVShowSeasonProxy(Playlist):

    objects = TVShowSeasonProxyManager()
    class Meta:
        proxy = True
        verbose_name = 'Season'
        verbose_name_plural = 'Seasons'

    def save(self, *args, **kwargs):
        self.type = Playlist.PlaylistTypeChoices.SEASON
        super().save(*args, **kwargs)

class MovieProxyManager(PlaylistManager):
    def all(self):
        return self.get_queryset().filter(type=Playlist.PlaylistTypeChoices.MOVIE)

class MovieProxy(Playlist):

    objects = MovieProxyManager()

    def __str__(self):
        return self.title
    class Meta:
        proxy = True
        verbose_name = 'Movie'
        verbose_name_plural = 'Movies'

    def save(self, *args, **kwargs):
        self.type = Playlist.PlaylistTypeChoices.MOVIE
        super().save(*args, **kwargs)

class PlaylistItem(models.Model):
    #playlist_obj.playlistitem_set.all() -> PlaylistItem.object.all()
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-timestamp']

    #qs = PlaylistItem.objects.filter(playlist=my_playlist_obj).order_by('order')


pre_save.connect(publish_state_pre_save, sender=TVShowProxy)
pre_save.connect(slugify_pre_save, sender=TVShowProxy)

pre_save.connect(publish_state_pre_save, sender=MovieProxy)
pre_save.connect(slugify_pre_save, sender=MovieProxy)

pre_save.connect(publish_state_pre_save, sender=TVShowSeasonProxy)
pre_save.connect(slugify_pre_save, sender=TVShowSeasonProxy)

pre_save.connect(publish_state_pre_save, sender=Playlist)
pre_save.connect(slugify_pre_save, sender=Playlist)