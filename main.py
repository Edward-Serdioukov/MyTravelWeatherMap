from flet import *
import flet
from flet import Page

from views.weather_view import TravelWeather


def main(page: Page):

    travel_weather = TravelWeather(page)
    travel_weather_cities_view = travel_weather.travel_weather_cities_view()
    travel_weather_map_view = travel_weather.travel_weather_map_view()
    
    def route_change(route):
        page.views.clear()
        if page.route == "/travel_weather":
            page.views.append( travel_weather_map_view)
        elif page.route == "/travel_weather_cities":
            page.views.append( travel_weather_cities_view)

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.go("/travel_weather")
    
#flet.app(target=main, assets_dir="assets", view=AppView.WEB_BROWSER, upload_dir="assets/images", port=8000)
#
flet.app(target=main, assets_dir="assets")
#flet.app(main) ###flet run --web main.py

