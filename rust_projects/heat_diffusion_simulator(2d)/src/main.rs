use ndarray::Array2 as nd;
use ndarray::s;
use std::mem :: swap;
use std::time::Instant;
use minifb::{Key, Scale, Window, WindowOptions};
use ndarray::Zip;
struct Mathpart{
    temperatures:nd<f32>,
    next_temps:nd<f32>
}
impl Mathpart{
    fn thermal(&mut self,xsize:usize,ysize:usize){
        let x:usize = 4;
        let y:usize = 150;
        let material_temps:f32 = 25.0;
        let specific_temp:f32 = 1000000000.0;
        self.temperatures = nd::from_elem((ysize,xsize),material_temps);
        self.next_temps = nd::from_elem((ysize,xsize),material_temps);
        self.temperatures[(y,x)] = specific_temp;
    }
    fn step(&mut self,xsize: usize,ysize: usize){
        let conductivity:f32 = 0.1;
        let center = self.temperatures.slice(s![1..ysize-1,1..xsize-1]);
        let top = self.temperatures.slice(s![0..ysize-2,1..xsize-1]);
        let bottom = self.temperatures.slice(s![2..ysize,1..xsize-1]);
        let left = self.temperatures.slice(s![1..ysize-1,0..xsize-2]);
        let right = self.temperatures.slice(s![1..ysize-1,2..xsize]);
        let mut temporary_array = self.next_temps.slice_mut(s![1..ysize-1,1..xsize-1]);
        Zip::from(&mut temporary_array)
        .and(&center)
        .and(&top)
        .and(&bottom)
        .and(&left)
        .and(&right)
        .for_each(|next_val, &center, &top, &bottom, &left, &right| {
            let laplacian = top + bottom + left + right - (4.0 * center);
            *next_val = center + (conductivity * laplacian);
        });
        // Apply Neumann (insulated) boundary conditions
        let top_row = self.next_temps.slice(s![1, ..]).to_owned();
        self.next_temps.slice_mut(s![0, ..]).assign(&top_row);

        let bottom_row = self.next_temps.slice(s![ysize - 2, ..]).to_owned();
        self.next_temps.slice_mut(s![ysize - 1, ..]).assign(&bottom_row);

        let left_col = self.next_temps.slice(s![.., 1]).to_owned();
        self.next_temps.slice_mut(s![.., 0]).assign(&left_col);

        let right_col = self.next_temps.slice(s![.., xsize - 2]).to_owned();
        self.next_temps.slice_mut(s![.., xsize - 1]).assign(&right_col);
        swap(&mut self.temperatures, &mut self.next_temps);
         }
    }
  

pub struct ThermalViewer {
    window: Window,
    buffer: Vec<u32>,
    xsize: usize,
    ysize: usize,
    min_temp: f32,
    max_temp: f32,
    last_frame_time: Instant,
}

impl ThermalViewer {
    pub fn new(xsize: usize, ysize: usize, scale: Scale) -> Self {
        let window = Window::new(
            "Thermal Heatmap",
            xsize,
            ysize,
            WindowOptions {
                scale,
                ..WindowOptions::default()
            },
        )
        .expect("Failed to create minifb window");

        ThermalViewer {
            window,
            buffer: vec![0; xsize * ysize],
            xsize,
            ysize,
            min_temp: -1000.0,
            max_temp: 1000.0,
            last_frame_time: Instant::now(),
        }
    }
    fn temp_to_color(&self, temp: f32) -> u32 {
    let norm = ((temp - self.min_temp) / (self.max_temp - self.min_temp)).clamp(0.0, 1.0);

    let (r, g, b) = if norm < 0.20 {
        // Cold: Blue -> Cyan
        let t = norm / 0.20;
        (0.0, t * 255.0, 255.0)
    } else if norm < 0.40 {
        // Cool: Cyan -> Green
        let t = (norm - 0.20) / 0.20;
        (0.0, 255.0, (1.0 - t) * 255.0)
    } else if norm < 0.60 {
        // Warm: Green -> Yellow
        let t = (norm - 0.40) / 0.20;
        (t * 255.0, 255.0, 0.0)
    } else if norm < 0.80 {
        // Hot: Yellow -> Red
        let t = (norm - 0.60) / 0.20;
        (255.0, (1.0 - t) * 255.0, 0.0)
    } else {
        // Extreme: Red -> Magenta/Purple (Bring Blue back up!)
        let t = (norm - 0.80) / 0.20;
        (255.0, 0.0, t * 255.0)
    };

    let red = r as u32;
    let green = g as u32;
    let blue = b as u32;

    (red << 16) | (green << 8) | blue
    }

    /// Convert the 2D temperature matrix to our 1D pixel buffer and push to screen
    pub fn draw(&mut self, grid: &nd<f32>) {
    // Calculate FPS
    let now = Instant::now();
    let delta = now.duration_since(self.last_frame_time).as_secs_f32();
    self.last_frame_time = now;
    
    let fps = if delta > 0.0 { 1.0 / delta } else { 0.0 };
    
    // Live-update title bar
    self.window.set_title(&format!("Thermal Heatmap | FPS: {:.1}", fps));

    for y in 0..self.ysize {
        for x in 0..self.xsize {
            let temp = grid[(y, x)];
            self.buffer[y * self.xsize + x] = self.temp_to_color(temp);
        }
    }

    self.window
        .update_with_buffer(&self.buffer, self.xsize, self.ysize)
        .unwrap();
    }

    /// Check if window is still open and ESC hasn't been pressed
    pub fn is_open(&self) -> bool {
        self.window.is_open() && !self.window.is_key_down(Key::Escape)
    }
}
fn main() {
    let xsize = 688;
    let ysize = 384;
    let max_steps:i32 = 1000000;
    let steps_per_frame = 50;
    let mut current_steps:i32 = 0;
    let mut sim = Mathpart {
        temperatures: nd::default((ysize, xsize)),
        next_temps: nd::default((ysize, xsize)),
    };
        sim.thermal(xsize,ysize);
    let mut viewer = ThermalViewer::new(xsize, ysize, minifb::Scale::X2,);
    while viewer.is_open() {
        if current_steps < max_steps {
            for _ in 0..steps_per_frame {
                sim.step(xsize, ysize);
                current_steps += 1;
                if current_steps >= max_steps {
                    break;
                }
            }
            // Render to screen once per batch
            viewer.draw(&sim.temperatures);
        } else {
            viewer.window.update();
        }
        }
    }   