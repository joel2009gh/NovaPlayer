#!/usr/bin/env python3
import os
import sys
import argparse
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import signal
import time
from PIL import Image, ImageTk
from datetime import datetime
import locale
import atexit
import psutil

active_processes = []
cleanup_called = False

class NovaPlayer:
    def __init__(self, url=None, headless=False, auto_record=False):
        self.url = url
        self.headless = headless
        self.auto_record = auto_record
        self.process = None
        self.record_process = None
        self.is_playing = False
        self.is_recording = False
        self.current_recording_file = None
        self.should_reconnect = True
        self.max_retries = 10
        self.retry_delay = 5
        
        atexit.register(self.cleanup_processes)
        
        try:
            locale.setlocale(locale.LC_TIME, 'nl_NL.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_TIME, 'nl_NL')
            except:
                pass
        
        self.recordings_dir = os.path.expanduser("~/Opnames")
        os.makedirs(self.recordings_dir, exist_ok=True)
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        if not headless:
            self.setup_gui()
        
        if url:
            self.play_url(url)
            if auto_record:
                self.start_recording()

    def signal_handler(self, sig, frame):
        print(f"Received signal {sig}, shutting down...")
        self.should_reconnect = False
        self.cleanup_and_exit()

    def cleanup_and_exit(self):
        self.should_reconnect = False
        self.on_stop()
        self.stop_recording()
        self.cleanup_processes()
        sys.exit(0)

    def cleanup_processes(self):
        global cleanup_called
        if cleanup_called:
            return
        cleanup_called = True
        print("Cleaning up processes...")
        
        self.should_reconnect = False
        
        if self.is_playing:
            self.on_stop()
        if self.is_recording:
            self.stop_recording()
        
        global active_processes
        for proc in active_processes[:]:
            try:
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        try:
                            proc.wait(timeout=1)
                        except subprocess.TimeoutExpired:
                            pass
                if proc in active_processes:
                    active_processes.remove(proc)
            except Exception as e:
                print(f"Error terminating process: {e}")

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("NovaPlayer")
        self.root.geometry("600x400")
        self.root.minsize(400, 300)
        self.root.configure(bg="#1e1e1e")

        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background='#1e1e1e')
        
        style.configure('TButton', 
                        background='#0078d7',
                        foreground='white',
                        font=('Segoe UI', 10, 'bold'),
                        padding=10,
                        relief='flat')
        style.map('TButton', 
                  background=[('active', '#005a9e')],
                  foreground=[('disabled', '#888888')])
        
        style.configure('TEntry', 
                        fieldbackground='#2a2a2a',
                        foreground='white',
                        insertcolor='white',
                        font=('Segoe UI', 10),
                        bordercolor='#0078d7',
                        borderwidth=1)

        style.configure('TLabel', 
                        background='#1e1e1e', 
                        foreground='white',
                        font=('Segoe UI', 10))
        
        style.configure('Status.TLabel', 
                        foreground='#4CAF50',
                        font=('Segoe UI', 10, 'bold')) 
        style.configure('RecordStatus.TLabel', 
                        foreground='#FFC107',
                        font=('Segoe UI', 10, 'bold'))
        
        top_frame = ttk.Frame(self.root, style='TFrame')
        top_frame.pack(pady=10, fill=tk.X)

        try:
            logo_path = "/usr/local/share/icons/novaplayer.png"
            if not os.path.exists(logo_path):
                script_dir = os.path.dirname(os.path.abspath(__file__))
                logo_path = os.path.join(script_dir, "assets", "NovaPlayer.png")
                if not os.path.exists(logo_path):
                    logo_path = os.path.join(script_dir, "NovaPlayer.png")
                    
            if os.path.exists(logo_path):
                img = Image.open(logo_path)
                img = img.resize((80, 80), Image.LANCZOS)
                logo_img = ImageTk.PhotoImage(img)
                logo_label = ttk.Label(top_frame, image=logo_img, background="#1e1e1e")
                logo_label.image = logo_img
                logo_label.pack()
            else:
                title_label = ttk.Label(top_frame, text="NovaPlayer", 
                                       font=('Segoe UI', 18, 'bold'), 
                                       background="#1e1e1e", foreground="white")
                title_label.pack()
        except Exception as e:
            print(f"Could not load logo: {e}")
            title_label = ttk.Label(top_frame, text="NovaPlayer", 
                                   font=('Segoe UI', 18, 'bold'), 
                                   background="#1e1e1e", foreground="white")
            title_label.pack()
            
        content_frame = ttk.Frame(self.root, style='TFrame', padding=(20, 10))
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        url_frame = ttk.Frame(content_frame, style='TFrame')
        url_frame.pack(fill=tk.X, pady=10)
        
        url_label = ttk.Label(url_frame, text="Stream URL:", style='TLabel')
        url_label.pack(side=tk.LEFT, padx=(0, 10), anchor=tk.W)
        
        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        if self.url:
            self.url_entry.insert(0, self.url)
            
        button_frame = ttk.Frame(content_frame, style='TFrame')
        button_frame.pack(pady=15)
        
        self.play_button = ttk.Button(button_frame, text="▶ Play", command=self.on_play)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="■ Stop", command=self.on_stop)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.record_button = ttk.Button(button_frame, text="● Record", command=self.toggle_recording)
        self.record_button.pack(side=tk.LEFT, padx=5)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(content_frame, textvariable=self.status_var, style='Status.TLabel')
        status_label.pack(pady=5, anchor=tk.CENTER)
        
        self.record_status_var = tk.StringVar(value="Niet aan het opnemen")
        record_status_label = ttk.Label(content_frame, textvariable=self.record_status_var, style='RecordStatus.TLabel')
        record_status_label.pack(pady=5, anchor=tk.CENTER)
        
        footer_frame = ttk.Frame(self.root, style='TFrame')
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 10))
        footer_label = ttk.Label(footer_frame, text="© 2025 NovaPlayer. All rights reserved.", 
                                 background="#1e1e1e", foreground="#888888", font=('Segoe UI', 8))
        footer_label.pack(pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_play(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a stream URL")
            return
        self.should_reconnect = True
        self.play_url(url)

    def play_url(self, url):
        self.url = url
        self.should_reconnect = True
        self.attempt_connection(0)

    def attempt_connection(self, retry_count):
        if not self.should_reconnect:
            return
        
        try:
            if self.process and self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.process.kill()
            
            if retry_count > 0:
                status_msg = f"Reconnecting... (attempt {retry_count + 1}/{self.max_retries + 1})"
            else:
                status_msg = "Connecting to stream..."
            
            if not self.headless and hasattr(self, 'status_var'):
                self.status_var.set(status_msg)
            else:
                print(f"NovaPlayer: {status_msg}")
            
            # SSL certificaat fix: voeg --http-cert-ignore toe
            cmd = ['cvlc', '--intf', 'dummy', '--quiet', '--http-cert-ignore', '--gnutls-system-trust', self.url]
            if self.headless:
                cmd.extend(['--no-video'])
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            global active_processes
            active_processes.append(self.process)
            self.is_playing = True
            
            threading.Thread(target=self.monitor_playback_with_retry, args=(retry_count,), daemon=True).start()
            
            if self.auto_record and not self.is_recording:
                self.start_recording()
                
        except Exception as e:
            error_msg = f"Error playing stream: {str(e)}"
            if self.headless:
                print(f"Error: {error_msg}")
            else:
                self.status_var.set(error_msg)
                messagebox.showerror("Error", error_msg)
            
            if self.should_reconnect and retry_count < self.max_retries:
                threading.Thread(target=self.schedule_retry, args=(retry_count + 1,), daemon=True).start()

    def schedule_retry(self, retry_count):
        if not self.should_reconnect:
            return
        
        status_msg = f"Retrying in {self.retry_delay} seconds... (attempt {retry_count + 1}/{self.max_retries + 1})"
        if not self.headless and hasattr(self, 'status_var'):
            self.status_var.set(status_msg)
        else:
            print(f"NovaPlayer: {status_msg}")
        
        time.sleep(self.retry_delay)
        
        if self.should_reconnect:
            self.attempt_connection(retry_count)

    def monitor_playback_with_retry(self, retry_count):
        if self.process:
            self.process.wait()
            
            if not self.should_reconnect:
                return
            
            if self.process.returncode == 0:
                status_msg = "Stream ended"
            else:
                stderr_output = self.process.stderr.read() if self.process.stderr else ""
                status_msg = f"Connection lost (code {self.process.returncode})"
                if stderr_output:
                    print(f"VLC error: {stderr_output}")
            
            self.is_playing = False
            
            if not self.headless and hasattr(self, 'status_var'):
                self.status_var.set(status_msg)
            else:
                print(f"NovaPlayer: {status_msg}")
            
            if self.should_reconnect and retry_count < self.max_retries:
                threading.Thread(target=self.schedule_retry, args=(retry_count + 1,), daemon=True).start()
            elif retry_count >= self.max_retries:
                final_msg = f"Max retries ({self.max_retries}) reached. Giving up."
                if not self.headless and hasattr(self, 'status_var'):
                    self.status_var.set(final_msg)
                else:
                    print(f"NovaPlayer: {final_msg}")

    def get_recording_filename(self):
        now = datetime.now()
        day = now.day
        month_name = now.strftime("%B")
        time_of_day = "avond" if now.hour >= 12 else "ochtend"
        filename = f"EXAMPLE {day} {month_name} {time_of_day}.mp3"
        return os.path.join(self.recordings_dir, filename)

    def start_recording(self):
        if self.is_recording:
            return
        
        try:
            url = self.url
            if not url:
                url = self.url_entry.get().strip() if hasattr(self, 'url_entry') else None
                
            if not url:
                raise ValueError("Geen URL om op te nemen")
                
            self.current_recording_file = self.get_recording_filename()
            
            # SSL certificaat fix ook voor opname
            cmd = ['cvlc', '--intf', 'dummy', '--quiet', '--http-cert-ignore', '--gnutls-system-trust', url, '--sout', f'#transcode{{acodec=mp3,ab=192}}:std{{access=file,mux=raw,dst={self.current_recording_file}}}', '--sout-keep']
            
            self.record_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            global active_processes
            active_processes.append(self.record_process)
            self.is_recording = True
            
            record_status = f"Opname gestart: {os.path.basename(self.current_recording_file)}"
            if not self.headless and hasattr(self, 'record_status_var'):
                self.record_status_var.set(record_status)
            else:
                print(f"NovaPlayer: {record_status}")
            
            threading.Thread(target=self.monitor_recording, daemon=True).start()
                
        except Exception as e:
            error_msg = f"Fout bij starten opname: {str(e)}"
            if self.headless:
                print(f"Error: {error_msg}")
            else:
                if hasattr(self, 'record_status_var'):
                    self.record_status_var.set(error_msg)
                messagebox.showerror("Opnamefout", error_msg)

    def stop_recording(self):
        if not self.is_recording or not self.record_process:
            return
        
        try:
            if self.record_process.poll() is None:
                self.record_process.terminate()
                try:
                    self.record_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.record_process.kill()
                    try:
                        self.record_process.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        pass
            
            self.is_recording = False
            record_status = "Opname gestopt"
            if not self.headless and hasattr(self, 'record_status_var'):
                self.record_status_var.set(record_status)
            else:
                print(f"NovaPlayer: {record_status}")
                
        except Exception as e:
            print(f"Fout bij stoppen opname: {str(e)}")

    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def monitor_recording(self):
        if self.record_process:
            self.record_process.wait()
            
            if self.record_process.returncode != 0:
                stderr_output = self.record_process.stderr.read() if self.record_process.stderr else ""
                error_msg = f"Opnamefout (code {self.record_process.returncode})"
                if stderr_output:
                    print(f"VLC error: {stderr_output}")
                
                if not self.headless and hasattr(self, 'record_status_var'):
                    self.record_status_var.set(error_msg)
                else:
                    print(f"NovaPlayer: {error_msg}")
            else:
                success_msg = "Opname succesvol voltooid."
                if not self.headless and hasattr(self, 'record_status_var'):
                    self.record_status_var.set(success_msg)
                else:
                    print(f"NovaPlayer: {success_msg}")
            
            self.is_recording = False

    def on_stop(self):
        self.should_reconnect = False
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    try:
                        self.process.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        pass
            except Exception as e:
                print(f"Error stopping playback: {e}")
        self.is_playing = False
        status_msg = "Stopped"
        if not self.headless and hasattr(self, 'status_var'):
            self.status_var.set(status_msg)
        else:
            print(f"NovaPlayer: {status_msg}")

    def on_close(self):
        self.on_stop()
        self.stop_recording()
        if hasattr(self, 'root'):
            self.root.destroy()

    def run(self):
        if self.headless:
            try:
                while self.is_playing or self.is_recording or (self.process and self.process.poll() is None) or (self.record_process and self.record_process.poll() is None):
                    time.sleep(1)
            except KeyboardInterrupt:
                print("NovaPlayer: Stopping playback and recording")
                self.on_stop()
                self.stop_recording()
            except Exception as e:
                print(f"NovaPlayer: Unexpected error in headless mode: {e}")
        else:
            self.root.mainloop()

def kill_orphaned_processes():
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] in ['vlc', 'cvlc']:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'NovaPlayer' in cmdline or 'dummy' in cmdline:
                        print(f"Killing orphaned process: {proc.pid} {proc.info['name']}")
                        proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        print(f"Error cleaning up orphaned processes: {e}")

def main():
    kill_orphaned_processes()
    parser = argparse.ArgumentParser(description='NovaPlayer - Stream URL Player')
    parser.add_argument('url', nargs='?', help='URL of the stream to play')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode (no GUI)')
    parser.add_argument('--record', action='store_true', help='Automatically start recording')
    args = parser.parse_args()
    player = NovaPlayer(url=args.url, headless=args.headless, auto_record=args.record)
    try:
        player.run()
    except KeyboardInterrupt:
        print("NovaPlayer: Received keyboard interrupt, shutting down...")
    except Exception as e:
        print(f"NovaPlayer: Unexpected error: {e}")
    finally:
        player.cleanup_processes()

if __name__ == "__main__":
    main()
