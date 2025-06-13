import requests
import json
from datetime import datetime, timedelta
from colorama import init, Fore, Back, Style

# Sbelumnyaa install Modul di terminal pip install requests colorama
# Initialize colorama
init()

class WeatherPredictor:
    def __init__(self):
        # Menggunakan wttr.in API - gratis tanpa registrasii
        self.base_url = "https://wttr.in"
        
        # Mapping kode cuaca ke bahasa Indonesia dan icon
        self.weather_translation = {
            "Sunny": ("Cerah", "☀️"),
            "Clear": ("Cerah", "🌞"), 
            "Partly cloudy": ("Berawan Sebagian", "⛅"),
            "Cloudy": ("Berawan", "☁️"),
            "Overcast": ("Mendung", "🌥️"),
            "Mist": ("Berkabut", "🌫️"),
            "Patchy rain possible": ("Kemungkinan Hujan Ringan", "🌦️"),
            "Light rain": ("Hujan Ringan", "🌧️"),
            "Moderate rain": ("Hujan Sedang", "🌧️"),
            "Heavy rain": ("Hujan Lebat", "⛈️"),
            "Thundery outbreaks possible": ("Kemungkinan Badai Petir", "⛈️"),
            "Light rain shower": ("Gerimis", "🌦️"),
            "Moderate or heavy rain shower": ("Hujan Deras", "⛈️"),
            "Patchy rain nearby": ("Hujan di Sekitar", "🌦️")
        }

    def get_forecast_data(self, city_name, forecast_type='today'):
        """Mengambil data prediksi cuaca (hari ini, mingguan, atau bulanan)"""
        url = f"{self.base_url}/{city_name}?format=j1"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                forecasts = []
                
                if forecast_type == 'today':
                    # Data hari ini (3 periode waktu)
                    current = data['current_condition'][0]
                    forecasts.append({
                        'datetime': datetime.now(),
                        'city': city_name.title(),
                        'weather': current['weatherDesc'][0]['value'],
                        'temperature': int(current['temp_C']),
                        'wind_speed': round(float(current['windspeedKmph']) * 0.278, 2),
                        'humidity': current['humidity'],
                        'feels_like': current['FeelsLikeC']
                    })
                    
                    # Tambah prediksi untuk jam berikutnyaa
                    if 'weather' in data and data['weather']:
                        today = data['weather'][0]
                        current_hour = datetime.now().hour
                        for hour in today['hourly']:
                            hour_time = int(hour['time']) // 100
                            if hour_time > current_hour and len(forecasts) < 3:
                                forecasts.append({
                                    'datetime': datetime.now().replace(hour=hour_time, minute=0),
                                    'city': city_name.title(),
                                    'weather': hour['weatherDesc'][0]['value'],
                                    'temperature': int(hour['tempC']),
                                    'wind_speed': round(float(hour['windspeedKmph']) * 0.278, 2),
                                    'humidity': hour['humidity'],
                                    'feels_like': hour['FeelsLikeC']
                                })
                
                elif forecast_type == 'weekly':
                    # Data mingguan (ini 7 hari ke depan)
                    if 'weather' in data:
                        for day in data['weather'][:7]:  # 7 hari ke depan
                            date = datetime.strptime(day['date'], '%Y-%m-%d')
                            # Ambil data tengah hari (index 4 = jam 12:00)
                            mid_day = day['hourly'][4]
                            forecasts.append({
                                'datetime': date,
                                'city': city_name.title(),
                                'weather': mid_day['weatherDesc'][0]['value'],
                                'temperature': int(mid_day['tempC']),
                                'wind_speed': round(float(mid_day['windspeedKmph']) * 0.278, 2),
                                'humidity': mid_day['humidity'],
                                'feels_like': mid_day['FeelsLikeC'],
                                'max_temp': int(day['maxtempC']),
                                'min_temp': int(day['mintempC'])
                            })
                
                elif forecast_type == 'monthly':
                    # Data bulanan (30 hari, dikelompokkan per minggu)
                    if 'weather' in data:
                        current_date = datetime.now()
                        for i in range(4):  # 4 minggu
                            week_temps = []
                            week_weather = []
                            for j in range(7):  # 7 hari per minggu
                                day_index = i * 7 + j
                                if day_index < len(data['weather']):
                                    day = data['weather'][day_index]
                                    week_temps.append(int(day['maxtempC']))
                                    week_weather.append(day['hourly'][4]['weatherDesc'][0]['value'])
                            
                            if week_temps and week_weather:
                                avg_temp = sum(week_temps) / len(week_temps)
                                most_common_weather = max(set(week_weather), key=week_weather.count)
                                week_start = current_date + timedelta(days=i*7)
                                week_end = week_start + timedelta(days=6)
                                
                                forecasts.append({
                                    'datetime': week_start,
                                    'end_date': week_end,
                                    'city': city_name.title(),
                                    'weather': most_common_weather,
                                    'temperature': round(avg_temp),
                                    'max_temp': max(week_temps),
                                    'min_temp': min(week_temps)
                                })
                
                return {'success': True, 'forecasts': forecasts}
            else:
                return {
                    'success': False,
                    'error': 'Kota tidak ditemukan atau kesalahan jaringan'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Gagal mengambil data: {str(e)}'
            }

    def translate_weather(self, weather_desc):
        """Menerjemahkan deskripsi cuaca ke bahasa Indonesia dan menambahkan icon"""
        translation = self.weather_translation.get(weather_desc, (weather_desc, "❓"))
        return f"{translation[0]} {translation[1]}"

    def display_predictions(self, predictions, forecast_type='today'):
        """Menampilkan prediksi cuaca dengan format yang menarik"""
        if forecast_type == 'today':
            self._display_today_forecast(predictions)
        elif forecast_type == 'weekly':
            self._display_weekly_forecast(predictions)
        else:  # monthly
            self._display_monthly_forecast(predictions)

    def _display_today_forecast(self, predictions):
        """Menampilkan prediksi cuaca hari ini"""
        for i, prediction in enumerate(predictions):
            weather_info = self.translate_weather(prediction['weather'])
            weather_text, weather_icon = weather_info.rsplit(' ', 1)
            
            colors = [Fore.CYAN, Fore.YELLOW, Fore.GREEN]
            current_color = colors[i % len(colors)]
            
            print(f"\n{current_color}{'='*50}{Style.RESET_ALL}")
            print(f"{current_color}Waktu{Style.RESET_ALL}: {Fore.WHITE}{prediction['datetime'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{current_color}Kota{Style.RESET_ALL}: {Fore.WHITE}{prediction['city']}")
            print(f"{current_color}Cuaca{Style.RESET_ALL}: {Fore.WHITE}{weather_text} {weather_icon}")
            print(f"{current_color}Suhu{Style.RESET_ALL}: {Fore.WHITE}{prediction['temperature']}°C")
            print(f"{current_color}Terasa seperti{Style.RESET_ALL}: {Fore.WHITE}{prediction.get('feels_like', '-')}°C")
            print(f"{current_color}Kelembaban{Style.RESET_ALL}: {Fore.WHITE}{prediction.get('humidity', '-')}%")
            print(f"{current_color}Kecepatan Angin{Style.RESET_ALL}: {Fore.WHITE}{prediction['wind_speed']} m/s")
            print(f"{current_color}{'='*50}{Style.RESET_ALL}")

    def _display_weekly_forecast(self, predictions):
        """Menampilkan prediksi cuaca mingguan"""
        print(f"\n{Fore.CYAN}📅 PREDIKSI CUACA MINGGUAN{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        for prediction in predictions:
            weather_info = self.translate_weather(prediction['weather'])
            weather_text, weather_icon = weather_info.rsplit(' ', 1)
            
            print(f"\n{Fore.YELLOW}Tanggal{Style.RESET_ALL}: {prediction['datetime'].strftime('%A, %d %B %Y')}")
            print(f"{Fore.YELLOW}Kota{Style.RESET_ALL}: {prediction['city']}")
            print(f"{Fore.YELLOW}Cuaca{Style.RESET_ALL}: {weather_text} {weather_icon}")
            print(f"{Fore.YELLOW}Suhu{Style.RESET_ALL}: {prediction['temperature']}°C (Min: {prediction['min_temp']}°C, Max: {prediction['max_temp']}°C)")
            print(f"{Fore.YELLOW}Kelembaban{Style.RESET_ALL}: {prediction.get('humidity', '-')}%")
            print(f"{Fore.YELLOW}Kecepatan Angin{Style.RESET_ALL}: {prediction['wind_speed']} m/s")
            print(f"{Fore.CYAN}{'-'*40}{Style.RESET_ALL}")

    def _display_monthly_forecast(self, predictions):
        """Menampilkan prediksi cuaca bulanan"""
        print(f"\n{Fore.MAGENTA}📅 PREDIKSI CUACA BULANAN (Per Minggu){Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        
        for i, prediction in enumerate(predictions, 1):
            weather_info = self.translate_weather(prediction['weather'])
            weather_text, weather_icon = weather_info.rsplit(' ', 1)
            
            print(f"\n{Fore.YELLOW}Minggu {i}{Style.RESET_ALL}")
            print(f"Periode: {prediction['datetime'].strftime('%d %B')} - {prediction['end_date'].strftime('%d %B %Y')}")
            print(f"Kota: {prediction['city']}")
            print(f"Cuaca: {weather_text} {weather_icon}")
            print(f"Rata-rata Suhu: {prediction['temperature']}°C")
            print(f"Range Suhu: {prediction['min_temp']}°C - {prediction['max_temp']}°C")
            print(f"{Fore.MAGENTA}{'-'*40}{Style.RESET_ALL}")

def display_welcome_banner():
    """Menampilkan banner selamat datang yang menarik"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║                  {Fore.YELLOW}🌞 SELAMAT DATANG DI 🌞{Fore.CYAN}                 ║
║              {Fore.YELLOW}APLIKASI PREDIKSI CUACA v1.0{Fore.CYAN}                ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.YELLOW}Fitur:{Style.RESET_ALL}
📍 Prediksi cuaca untuk kota di seluruh dunia
🌡️ Informasi suhu dan kelembaban udara
💨 Kecepatan angin dalam m/s
🌤️ Kondisi cuaca dengan icon
📅 Prediksi harian, mingguan, dan bulanan

{Fore.CYAN}Dibuat dengan ❤️  menggunakan Python & wttr.in{Style.RESET_ALL}
"""
    print(banner)

def main():
    """Fungsi utama untuk menjalankan program prediksi cuaca"""
    display_welcome_banner()
    
    while True:
        try:
            print(f"\n{Fore.CYAN}Pilih jenis prediksi:{Style.RESET_ALL}")
            print(f"1. {Fore.GREEN}Hari ini{Style.RESET_ALL} (3 periode waktu)")
            print(f"2. {Fore.YELLOW}Mingguan{Style.RESET_ALL} (7 hari ke depan)")
            print(f"3. {Fore.MAGENTA}Bulanan{Style.RESET_ALL} (4 minggu ke depan)")
            print(f"q. {Fore.RED}Keluar{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.GREEN}Pilihan Anda{Style.RESET_ALL}: ").lower()
            
            if choice == 'q':
                print(f"\n{Fore.YELLOW}Terima kasih telah menggunakan Aplikasi Prediksi Cuaca!{Style.RESET_ALL} 👋\n")
                break
            
            if choice not in ['1', '2', '3']:
                print(f"{Fore.RED}❌ Pilihan tidak valid. Silakan coba lagi.{Style.RESET_ALL}")
                continue
            
            city_name = input(f"\n{Fore.GREEN}Masukkan Nama Kota{Style.RESET_ALL}: ")
            
            # Buat instance weather predictor
            predictor = WeatherPredictor()
            
            # Tentukan jenis prediksi
            forecast_type = {
                '1': 'today',
                '2': 'weekly',
                '3': 'monthly'
            }[choice]
            
            print(f"\n{Fore.CYAN}🌤️  Mengambil data cuaca untuk {city_name}...{Style.RESET_ALL}")
            
            # Ambil prediksi cuaca
            forecast_result = predictor.get_forecast_data(city_name, forecast_type)
            
            if forecast_result['success']:
                print(f"{Fore.GREEN}✅ Berhasil mengambil data cuaca!{Style.RESET_ALL}")
                predictor.display_predictions(forecast_result['forecasts'], forecast_type)
            else:
                print(f"{Fore.RED}❌ Error: {forecast_result['error']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}💡 Tips: Pastikan nama kota benar dan koneksi internet stabil.{Style.RESET_ALL}")
            
            # Tanya apakah ingin mencoba lagi
            input(f"\n{Fore.CYAN}Tekan Enter untuk melanjutkan...{Style.RESET_ALL}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Program dihentikan oleh user.{Style.RESET_ALL} 👋\n")
            break
        except Exception as e:
            print(f"\n{Fore.RED}❌ Terjadi kesalahan: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Silakan coba lagi...{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
