from django.test import TestCase
from .models import Video

# Create your tests here.
class VideModelTestCase(TestCase):
    def setUp(self):
        Video.objects.create(title='This is My Title')
        Video.objects.create(title='This is My Title',state=Video)

    def test_draft_case(self):
        qs = Video.objects.filter(state=VideoStateOptions.DRAFT)
        self.assertEquals(qs.count(),1)

    def test_valid_title(self):
        title = 'This Is My Title'
        qs = Video.objects.filter(title=title)
        self.assertTrue(qs.exists())