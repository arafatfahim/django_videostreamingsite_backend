from django.shortcuts import render
from django.http import Http404
from django.views.generic import ListView, DetailView

# Create your views here.
from  .models import  MovieProxy, TVShowProxy, Playlist, TVShowSeasonProxy

class PlaylistMixin():
    template_name = 'playlist_list.html'
    title = None
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.title is not None:
            context['title'] = self.title
        print (context)
        return context

    def get_queryset(self):
        return super().get_queryset().published()


class MovieListView(PlaylistMixin, ListView):
    queryset = MovieProxy.objects.all()
    title =  "Movies"
    
class MovieDetailView(PlaylistMixin, DetailView):
    template_name = 'playlists/movie_detail.html'
    queryset = MovieProxy.objects.all()
    

class PlaylistDetailView(PlaylistMixin, DetailView):
    template_name = 'playlists/playlist_detail.html'
    queryset = Playlist.objects.all()

    def  get_object(self):
        request = self.request
        kwargs =self.kwargs
        print (request, kwargs)
        return self.get_queryset().filter(**kwargs).first()
    
class TVShowListView(PlaylistMixin, ListView):
    queryset = TVShowProxy.objects.all()
    title = "TV Shows"

class TVShowDetailView(PlaylistMixin, DetailView):
    template_name = 'playlists/tvshow_detail.html'
    queryset = TVShowProxy.objects.all()


class TVShowSeasonDetailView(PlaylistMixin, DetailView):
    template_name = 'playlists/tvshow_detail.html'
    queryset = TVShowProxy.objects.all()

    def get_object(self):
        kwargs = self.kwargs
        show_slug = kwargs.get("showSlug")
        season_slug = kwargs.get("seasonSlug")
        qs = self.get_queryset().filter(parent__slug__iexact = show_slug, slug__iexact=season_slug)
        if not qs.count() == 1:
            raise Exception("Not Found")
        return qs.first()


class FeturedPlaylistListView(PlaylistMixin, ListView):
    queryset = Playlist.objects.fetured_playlists()
    title = "Featured Playlist"