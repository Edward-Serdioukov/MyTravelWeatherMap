import base64
import re
import flet.map as map
from flet import (
    View,
    Container,
    Text,
    Column,
    Row,
    colors,
    Card,
    Image,
    AppBar,
    IconButton,
    MainAxisAlignment,
    ThemeMode,
    AlertDialog,
    TextButton,
    FontWeight,
    icons,
    alignment,
    NavigationBar,NavigationBarDestination,
    DataTable, DataColumn, DataRow, DataCell,
)
import flet
import requests
from tinydb import TinyDB, Query

from weather import get_geo_data, get_weather_day

class TravelWeather():

    def __init__(self, page):
        self.db = TinyDB('db.json')
        self.City = Query()
        self.page = page    
        self.page.theme_mode = ThemeMode.LIGHT
       

        self.navbar = NavigationBar(
            destinations=[
                NavigationBarDestination(icon=icons.MAP, label="Map"),
                NavigationBarDestination(icon=icons.SETTINGS, label="Settings"),
            ],
            on_change=lambda e: self.navbar_event(e),
        )
        
        self.marker_layer_ref = flet.Ref[map.MarkerLayer]()
        self.circle_layer_ref = flet.Ref[map.CircleLayer]()
        self.markers = [] 
        

        self.weather_travel_map = map.Map(
            expand=True,
            configuration=map.MapConfiguration(
                initial_center=map.MapLatitudeLongitude(48, 20),
                initial_zoom=3.6,
                interaction_configuration=map.MapInteractionConfiguration(
                    flags=map.MapInteractiveFlag.ALL
                ),
                on_init=lambda e: print(f"Initialized Map"),
            ),
            layers=[
                map.TileLayer(
                    url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    on_image_error=lambda e: print("TileLayer Error"),
                ),
                map.MarkerLayer(
                    ref=self.marker_layer_ref,
                    markers = self.markers,
                ), 
            ],
        )
        self.progress_ring = flet.ProgressRing(stroke_width = 5)

        self.splash = Container(
            content=self.progress_ring,
            expand=True,
            alignment=alignment.center,
            visible=False
        )
        self.page.overlay.append(self.splash)
        
    def navbar_event(self, e):
        if e.control.selected_index == 0:
            self.page.go("/travel_weather")	
        if e.control.selected_index ==1:
            self.page.go("/travel_weather_cities")



    def travel_weather_map_clicked(self, e):
        self.refresh_map_markers()
                
    def refresh_map_markers(self):
        self.show_progress()
        self.markers.clear()
        self.create_map()
        self.hide_progress()
        self.page.update()

    def show_progress(self):
        self.splash.visible = True
        self.page.update()

    def hide_progress(self):
        self.splash.visible = False
        self.page.update()
        
    def theme_changed(self, e):
        if self.page.theme_mode == ThemeMode.LIGHT:
            self.page.theme_mode = ThemeMode.DARK
        else:
            self.page.theme_mode = ThemeMode.LIGHT

        self.page.update()
       
        
    def load_image_from_url(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')
        else:
            print(f"Failed to load image. Status code: {response.status_code}")
            return None
    
            
    def show_image_modal(self, e):

        def close_dlg(e):

            dlg_modal.open = False
            self.page.update()

        # Create the content of the modal dialog
        try:
            weather_day = get_weather_day(e.control.data['name'])
            if weather_day is not None:

                image = Card(
                    elevation=1,
                    color=colors.BLUE_GREY_100,
                    content=Image(src_base64=self.load_image_from_url(weather_day['icon']), width=200, height=200)  )

                temperature = Text(f"{weather_day["temperature"]}°C", size=20, weight=FontWeight.BOLD)
                description = Text(weather_day["description"], no_wrap=False, size=20, weight=FontWeight.BOLD)

                # Create the modal dialog
                dlg_modal = AlertDialog(
                    modal=True,
                    title=Text(e.control.data['name']),
                    content=Container(Column([image, temperature, description],
                                                alignment=flet.MainAxisAlignment.START,
                                                horizontal_alignment=flet.CrossAxisAlignment.CENTER,
                                                scroll=flet.ScrollMode.ALWAYS,),),
                    actions=[TextButton("Ok", data=e.control.data, on_click=lambda e: close_dlg(e))],
                    actions_alignment=MainAxisAlignment.END,
                )           
                # Show the modal dialog
                self.page.dialog = dlg_modal
                dlg_modal.open = True
                self.page.update()
            else:
                print(f"Failed to load image for city: {e.control.data['name']}")
        except Exception as e:
            print(f"Failed to load image for city: {e}")


    def create_map(self):
        data = self.db.all()   

        for city in self.db.all():
            marker = map.Marker(
                            content=Container(content=Image(src="images/location2.png",#"images/location2-red.png" if city['comp'] else "images/location2.png",
                                                            width=345, height=345),
                                            alignment=flet.alignment.center,
                                            data=city,  width=345, height=345,
                                            on_click=lambda e: self.show_image_modal(e),
                                            tooltip=flet.Tooltip(
                                                message=f"{city["name"]}",
                                                padding=20,
                                                border_radius=10,
                                                bgcolor=colors.WHITE,
                                                shadow=flet.BoxShadow(spread_radius=5, blur_radius=5, color=colors.BLACK),
                                                text_style=flet.TextStyle(size=20, color=colors.BLACK)
                                            )),
                            
                            coordinates=map.MapLatitudeLongitude(city["lat"], city["lon"]),
                            
                        )
            self.markers.append(marker)
    
    def travel_weather_map_view(self):
        appbar = AppBar(

            title=Text("MTW"), 
            center_title=False,
            actions=[
                IconButton(icon=flet.icons.REFRESH_OUTLINED, tooltip="Refresh", on_click=self.travel_weather_map_clicked),
            ],
        )
        self.create_map()                                            
        return View(
            route="/travel_weather",
            controls=[
                appbar,
                self.weather_travel_map,
                self.navbar
            ]
        )


    def travel_weather_cities_view(self):

        input_name = flet.TextField(label="Name of City")
        city_name = Text("")
    
        mytable =  DataTable(
            columns=[
                DataColumn(Text("City")),
                DataColumn(Text("Delete")),
            ],
            rows=[]
        )

        
        def recreate_datatable():
            data = self.db.all()
            mytable.rows.clear()
            for city in data:
                mytable.rows.append(
                    DataRow(
                    cells=[
                        DataCell(Text(city['name'])),
                        DataCell(IconButton(icon=flet.icons.DELETE, data=city, on_click=lambda e:removeitem(e))),
                    ],
                    )
                )
            return mytable
       
        def removeitem(e):
            self.db.remove(self.City.name == e.control.data['name'])
            recreate_datatable()
            self.page.snack_bar = flet.SnackBar(
                Text(f"succes delete city  = {e.control.data['name']}. Refresh the Map",color="white"),
                bgcolor="red",
                )
            self.page.snack_bar.open = True

            self.page.update()
 
        def addnewdata(e):
            geo_data = get_geo_data(input_name.value)
            if geo_data is not None:
                if not self.db.search(self.City.name.matches(input_name.value, flags=re.IGNORECASE)):
                    self.db.insert({'name': input_name.value, 'lat': geo_data[0], 'lon': geo_data[1], 'comp': False})
                    recreate_datatable()
            
                    self.page.snack_bar = flet.SnackBar(
                        Text(f"succes add city {input_name.value}. Refresh the Map",color="white"),
                        bgcolor="green",
                    )

                else:
                    self.page.snack_bar = flet.SnackBar(
                        Text(f"city {input_name.value} is already in the database",color="white"),
                        bgcolor="red",)
            else:
                self.page.snack_bar = flet.SnackBar(
                    Text(f"city {input_name.value} not found",color="white"),
                    bgcolor="red",)
                
            self.page.snack_bar.open = True
            input_name.value = ""
            self.page.update()
    
            
            
        addButton =  flet.ElevatedButton("add new",
            bgcolor="blue",
            color="white",
            on_click=addnewdata
            )

        
        recreate_datatable()
        
        appbar = AppBar(
            leading_width=40,
            title=Text("Settings"), 
            center_title=False,
            bgcolor=colors.SURFACE_VARIANT,
            actions=[
                IconButton(icon=flet.icons.WB_SUNNY_OUTLINED, on_click=self.theme_changed)
            ],
        )

        return View(
            route="/travel_weather_cities",
            scroll=flet.ScrollMode.AUTO,
            controls=[
                appbar,
                Column([
                    input_name,
                    Row([addButton]),
                    mytable,
                    ]),
                
                self.navbar
            ]
        )
