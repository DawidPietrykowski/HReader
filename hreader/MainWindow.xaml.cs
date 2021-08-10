using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Forms;
using System.Windows.Input;
using System.Windows.Interop;
using System.Windows.Media;

namespace hreader
{
    public partial class MainWindow : Window
    {
        public bool running = false;
        public int v = 0;
        public Process hreader = new Process();
        public int[] progress = new int[9] { 5, 10, 12, 65, 70, 95, 100, 100, 100 };
        public MainWindow()
        {
            InitializeComponent();
            LoadSettings();
            Settings(this, new RoutedEventArgs { });
            RenderOptions.ProcessRenderMode = RenderMode.SoftwareOnly;
            Process[] pname = Process.GetProcessesByName(System.IO.Path.GetFileNameWithoutExtension("fdash.exe"));
            foreach (Process p in pname)
            {
                if (!p.HasExited)
                {
                    p.Kill();
                    p.Dispose();
                }
            }


        }
        protected override void OnMouseLeftButtonDown(MouseButtonEventArgs e)
        {
            base.OnMouseLeftButtonDown(e);

            this.DragMove();
        }
        private void BrowseDirectory(object sender, RoutedEventArgs e)
        {
            var folderBrowserDialog1 = new FolderBrowserDialog();
            DialogResult result = folderBrowserDialog1.ShowDialog();
            if (result == System.Windows.Forms.DialogResult.OK)
            {
                Properties.Settings.Default.Directory = folderBrowserDialog1.SelectedPath;
                FileNameTextBox.Text = Properties.Settings.Default.Directory;
            }
        }

        private void DirectoryChanged(object sender, TextChangedEventArgs e)
        {
            Properties.Settings.Default.Directory = FileNameTextBox.Text;

        }

        private void OnApplicationExit(object sender, EventArgs e)
        {
            try
            {
                AppClose(this, new EventArgs { });
                SaveSettings();
            }
            catch { }
        }

        private void SaveSettings()
        {
            Properties.Settings.Default.Directory = FileNameTextBox.Text;
            Properties.Settings.Default.Language = LanguageSelect.SelectedIndex;
            Properties.Settings.Default.Mode = ModeBox.SelectedIndex;
            Properties.Settings.Default.Name = NameTextBox.Text;
            Properties.Settings.Default.Trimming = TrimCheckbox.IsChecked ?? true;
            Properties.Settings.Default.Resolution = ResTextBox.Text.ToString();
            Properties.Settings.Default.Trimlimit = TrimlimitTextBox.Text.ToString();
            Properties.Settings.Default.CommonWords = WordNBox.Text.ToString();
            Properties.Settings.Default.Color1 = chatter1colorpicker.SelectedColor.ToString();
            Properties.Settings.Default.Color2 = chatter2colorpicker.SelectedColor.ToString();
            Properties.Settings.Default.Save();

        }
        private void LoadSettings()
        {
            FileNameTextBox.Text = Properties.Settings.Default.Directory;
            LanguageSelect.SelectedIndex = Properties.Settings.Default.Language;
            ModeBox.SelectedIndex = Properties.Settings.Default.Mode;
            NameTextBox.Text = Properties.Settings.Default.Name;
            TrimCheckbox.IsChecked = Properties.Settings.Default.Trimming;
            ResTextBox.Text = Properties.Settings.Default.Resolution;
            TrimlimitTextBox.Text = Properties.Settings.Default.Trimlimit;
            WordNBox.Text = Properties.Settings.Default.CommonWords;
            chatter1colorpicker.SelectedColor = (Color)ColorConverter.ConvertFromString(Properties.Settings.Default.Color1);
            chatter2colorpicker.SelectedColor = (Color)ColorConverter.ConvertFromString(Properties.Settings.Default.Color2);
        }
        private void StartDashboard(object sender, RoutedEventArgs f)
        {
            if (running)
                return;

            if (!Directory.Exists(Properties.Settings.Default.Directory))
            {
                UpdateCls("directory " + Properties.Settings.Default.Directory + " doesn't exist");
                return;
            }

            hreader = new Process();

            hreader.StartInfo = new ProcessStartInfo();

            hreader.StartInfo.RedirectStandardOutput = true;
            hreader.StartInfo.CreateNoWindow = true;
            hreader.StartInfo.RedirectStandardError = true;
            hreader.StartInfo.RedirectStandardInput = true;
            hreader.StartInfo.UseShellExecute = false;
            Directory.SetCurrentDirectory(AppDomain.CurrentDomain.BaseDirectory + "\\fdash");
            hreader.StartInfo.FileName = "fdash.exe";
            hreader.StartInfo.WindowStyle = ProcessWindowStyle.Normal;

            string langselect = (LanguageSelect.SelectedItem.ToString()) switch
            {
                string a when a.Contains("Polish") => "pl",
                string b when b.Contains("English") => "en",
                _ => "en",
            };

            string Name = "\"" + normalize(NameTextBox.Text) + "\"";

            char textcolor = getColor(chatter2colorpicker.SelectedColor ?? Color.FromRgb(255, 255, 255));
            
            string args =
                Name
                + " \"" + Properties.Settings.Default.Directory + "\" "
                + langselect + " "
                + TrimCheckbox.IsChecked.ToString().ToLower() + " "
                + ResTextBox.Text.ToString() + " "
                + TrimlimitTextBox.Text.ToString() + " "
                + ModeBox.SelectedItem.ToString().Substring(38, 4).ToLower() + " "
                + "15" + " "
                + WordNBox.Text.ToString() + " "
                + chatter1colorpicker.SelectedColor.ToString().Replace("#FF", "#") + " " + chatter2colorpicker.SelectedColor.ToString().Replace("#FF", "#") + " "
                + textcolor;

            hreader.StartInfo.Arguments = args;

            hreader.OutputDataReceived += new DataReceivedEventHandler((s, e) =>
            {
                if (e.Data != null && e.Data.Length > 0)
                {
                    if (e.Data.Substring(0, 1) != "E")
                    {
                        UpdateCls(e.Data);
                    }
                    else
                    {
                        int eN = Int32.Parse(e.Data.Substring(1, 1));
                        switch (eN)
                        {
                            case 1:
                                UpdateCls("conversation not found");
                                break;
                            case 2:
                                UpdateCls("language file not found");
                                break;
                            case 3:
                                UpdateCls("language directory not found");
                                break;
                            case 4:
                                UpdateCls("language file reading error");
                                break;
                            case 5:
                                UpdateCls("essential file error");
                                break;
                            case 6:
                                UpdateCls("trimming exclusions file error");
                                break;
                            case 7:
                                UpdateCls("too few messages for this resolution");
                                break;
                        }

                        Process[] pname = Process.GetProcessesByName(System.IO.Path.GetFileNameWithoutExtension("fdash.exe"));
                        foreach (Process p in pname)
                        {
                            p.Kill();
                            p.Dispose();
                            this.Dispatcher.Invoke(() =>
                            {
                                StatusBlock.Text = "Status: not running";
                                running = false;
                                Progress.Value = 100;
                                v = 0;
                                Progress.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#FFFF3232"));
                            });
                        }

                        // UpdateCls("ERROR " + eN);
                    }
                }
            });
            hreader.ErrorDataReceived += new DataReceivedEventHandler((s, e) =>
            {
                if (e.Data != null)
                {
                    //UpdateCls(e.Data);

                    if (e.Data.Contains("Exception"))
                    {
                        int eN = Int32.Parse(e.Data.Substring(1, 1));
                        switch (eN)
                        {
                            case 1:
                                UpdateCls("conversation not found");
                                break;
                            case 2:
                                UpdateCls("language file not found");
                                break;
                            case 3:
                                UpdateCls("language directory not found");
                                break;
                            case 4:
                                UpdateCls("language file reading error");
                                break;
                            case 5:
                                UpdateCls("essential file error");
                                break;
                            case 6:
                                UpdateCls("trimming exclusions file error");
                                break;
                            case 7:
                                UpdateCls("too few messages for this resolution");
                                break;
                        }

                        Process[] pname = Process.GetProcessesByName(System.IO.Path.GetFileNameWithoutExtension("fdash.exe"));
                        foreach (Process p in pname)
                        {
                            p.Kill();
                            p.Dispose();
                            this.Dispatcher.Invoke(() =>
                            {
                                StatusBlock.Text = "Status: not running";
                                running = false;
                                Progress.Value = 100;
                                v = 0;
                                Progress.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#FFFF3232"));
                            });
                        }
                    }
                }
            });

            hreader.Start();
            hreader.BeginOutputReadLine();
            hreader.BeginErrorReadLine();
            running = true;
            StatusBlock.Text = "Status: running";
            Progress.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#FF06B025"));
            Progress.Value = 0;
            exedir.Text = "";
            SaveSettings();
        }

        public void UpdateCls(string e)
        {
            if (e != null)
            {
                if ((e.Contains('*') == false) && (e.Contains('[') == false) && (e.Contains("WARNING") == false) && (e.Contains("WSGI") == false))
                {
                    this.Dispatcher.Invoke(() =>
                    {
                        exedir.Text += e + '\n';
                        Progress.Value = progress[v];
                        v++;
                    });
                }
                if (e.Contains("Debug"))
                {
                    this.Dispatcher.Invoke(() =>
                    {
                        //exedir.Text += "dashboard running on http://127.0.0.1:8050/\n";
                        Process.Start("http://127.0.0.1:8050/");
                        Progress.Value = 100;
                    });
                }

            }
        }

        private void Close(object sender, RoutedEventArgs e)
        {
            if (running)
            {
                Process[] pname = Process.GetProcessesByName(System.IO.Path.GetFileNameWithoutExtension("fdash.exe"));
                foreach (Process p in pname)
                {
                    p.Kill();
                    p.Dispose();
                    this.Dispatcher.Invoke(() =>
                    {
                        if (!exedir.Text.Contains("dashboard closed"))
                            exedir.Text += "dashboard closed\n";
                        StatusBlock.Text = "Status: not running";
                        running = false;
                        Progress.Value = 100;
                        v = 0;
                        Progress.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#FFFF3232"));
                    });
                }
            }
        }

        private void AppClose(object sender, EventArgs e)
        {
            Process[] pname = Process.GetProcessesByName(System.IO.Path.GetFileNameWithoutExtension("fdash.exe"));
            foreach (Process p in pname)
            {
                if (!p.HasExited)
                {
                    p.Kill();
                    p.Dispose();
                }
            }
        }

        private static readonly Regex _regex = new Regex("[^0-9]+");
        private static bool IsTextAllowed(string text)
        {
            return _regex.IsMatch(text);
        }
        private void Resolution_PreviewTextInput(object sender, TextCompositionEventArgs e)
        {
            e.Handled = IsTextAllowed(e.Text);
        }

        private void OpenCommonWords(object sender, RoutedEventArgs e)
        {
            Directory.SetCurrentDirectory(AppDomain.CurrentDomain.BaseDirectory + "\\fdash\\lang");
            string langselect = (LanguageSelect.SelectedItem.ToString()) switch
            {
                string a when a.Contains("Polish") => "pl",
                string b when b.Contains("English") => "en",
                _ => "en",
            };
            Process.Start(langselect + ".txt");
        }

        private void OpenTrimExclusions(object sender, RoutedEventArgs e)
        {
            Directory.SetCurrentDirectory(AppDomain.CurrentDomain.BaseDirectory + "\\fdash\\lang");
            Process.Start("trimexclusions.txt");
        }

        private void Exit(object sender, RoutedEventArgs e)
        {
            SaveSettings();
            AppClose(this, e);
            System.Windows.Application.Current.Shutdown();
        }

        private void Minimize(object sender, RoutedEventArgs e)
        {
            WindowState = WindowState.Minimized;
        }

        private void Settings(object sender, RoutedEventArgs e)
        {
            if (SettingsCheckbox.IsChecked == true)
            {
                this.Dispatcher.Invoke(() =>
                {
                    System.Windows.Application.Current.MainWindow.Height = 490;
                    AdvSettings.Visibility = System.Windows.Visibility.Visible;
                });
            }
            else
            {
                this.Dispatcher.Invoke(() =>
                {
                    System.Windows.Application.Current.MainWindow.Height = 375;
                    AdvSettings.Visibility = System.Windows.Visibility.Hidden;
                });
            }
        }

        private void TrimmingPopup_MouseEnter(object sender, System.Windows.Input.MouseEventArgs e) { TrimmingPopup.IsOpen = true; }
        private void TrimmingPopup_MouseLeave(object sender, System.Windows.Input.MouseEventArgs e) { TrimmingPopup.IsOpen = false; }
        private void LangPopup_MouseLeave(object sender, System.Windows.Input.MouseEventArgs e) { LangPopup.IsOpen = false; }
        private void LangPopup_MouseEnter(object sender, System.Windows.Input.MouseEventArgs e) { LangPopup.IsOpen = true; }
        private void ModePopup_MouseLeave(object sender, System.Windows.Input.MouseEventArgs e) { ModePopup.IsOpen = false; }
        private void ModePopup_MouseEnter(object sender, System.Windows.Input.MouseEventArgs e) { ModePopup.IsOpen = true; }
        private void ResolutionPopup_MouseLeave(object sender, System.Windows.Input.MouseEventArgs e) { ResolutionPopup.IsOpen = false; }
        private void ResolutionPopup_MouseEnter(object sender, System.Windows.Input.MouseEventArgs e) { ResolutionPopup.IsOpen = true; }
        private void ColumnPopup_MouseLeave(object sender, System.Windows.Input.MouseEventArgs e) { ColumnPopup.IsOpen = false; }
        private void ColumnPopup_MouseEnter(object sender, System.Windows.Input.MouseEventArgs e) { ColumnPopup.IsOpen = true; }
        private void TrimlimitPopup_MouseLeave(object sender, System.Windows.Input.MouseEventArgs e) { TrimlimitPopup.IsOpen = false; }
        private void TrimlimitPopup_MouseEnter(object sender, System.Windows.Input.MouseEventArgs e) { TrimlimitPopup.IsOpen = true; }
        private void ColorPopup_MouseLeave(object sender, System.Windows.Input.MouseEventArgs e) { ColorPopup.IsOpen = false; }
        private void ColorPopup_MouseEnter(object sender, System.Windows.Input.MouseEventArgs e) { ColorPopup.IsOpen = true; }
        private void TrimEditPopup_MouseLeave(object sender, System.Windows.Input.MouseEventArgs e) { TrimEditPopup.IsOpen = false; }
        private void TrimEditPopup_MouseEnter(object sender, System.Windows.Input.MouseEventArgs e) { TrimEditPopup.IsOpen = true; }
        private void CommonWordsPopup_MouseLeave(object sender, System.Windows.Input.MouseEventArgs e) { CommonWordsPopup.IsOpen = false; }
        private void CommonWordsPopup_MouseEnter(object sender, System.Windows.Input.MouseEventArgs e) { CommonWordsPopup.IsOpen = true; }

        private char normalizeChar(char c)
        {
            switch (c)
            {
                case 'ą':
                    return 'a';
                case 'ć':
                    return 'c';
                case 'ę':
                    return 'e';
                case 'ł':
                    return 'l';
                case 'ń':
                    return 'n';
                case 'ó':
                    return 'o';
                case 'ś':
                    return 's';
                case 'ż':
                    return 'z';
                case 'ź':
                    return 'z';
            }
            return c;
        }

        private String normalize(String word)
        {
            if (word == null || "".Equals(word))
            {
                return word;
            }
            char[] charArray = word.ToCharArray();
            char[] normalizedArray = new char[charArray.Length];
            for (int i = 0; i < normalizedArray.Length; i++)
            {
                normalizedArray[i] = normalizeChar(charArray[i]);
            }
            return new String(normalizedArray);
        }

        private char getColor(Color c)
        {
            var r = c.R;
            var g = c.G;
            var b = c.B;

            var yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;

            if (yiq >= 160)
                return '0';
            else
                return '1';
        }
    }
}