use ndarray::Array2 as nd;
use ndarray::s;
use std::mem :: swap;
use std::time::Instant;
use minifb::{Key, Scale, Window, WindowOptions};
use ndarray::Zip;
use ndarray::ArrayView2;
use ndarray::ArrayViewMut2;
use ndarray::parallel::prelude::*;
struct Mathpart{
    temperatures:nd<f32>,
    next_temps:nd<f32>,
    vx:nd<f32>,
    vy:nd<f32>,
    density:nd<f32>,
    pressure:nd<f32>,
    next_vx:nd<f32>,
    next_vy:nd<f32>,
    next_density:nd<f32>,
    next_pressure:nd<f32>

}
impl Mathpart{
    fn thermal(&mut self,xsize:usize,ysize:usize){
        let x:usize = 101;
        let y:usize = 100;
        let pressure:f32 = 1.0;
        let density:f32 = 1.225;
        let vx:f32 = 0.001;
        let vy:f32 = 0.001;
        let material_temps:f32 = 298.0;
        let specific_temps:f32 = 398.0;
        self.vx = nd::from_elem((ysize,xsize), vx);
        self.vy = nd::from_elem((ysize,xsize), vy);
        self.density = nd::from_elem((ysize,xsize), density);
        self.pressure = nd::from_elem((ysize,xsize), pressure);
        self.next_vx = nd::from_elem((ysize,xsize), vx);
        self.next_vy = nd::from_elem((ysize,xsize), vy);
        self.next_density = nd::from_elem((ysize,xsize), density);
        self.next_pressure = nd::from_elem((ysize,xsize), pressure);
        self.temperatures = nd::from_elem((ysize,xsize),material_temps);
        self.next_temps = nd::from_elem((ysize,xsize),material_temps);
        self.temperatures[(y,x)] = specific_temps;
    }
    fn neighbours_view(grid:&nd<f32>,xsize: usize,ysize: usize)->(
        ArrayView2<'_, f32>,
        ArrayView2<'_, f32>,
        ArrayView2<'_, f32>,
        ArrayView2<'_, f32>,
    ArrayView2<'_, f32>,
    ) {
        let center: ndarray::prelude::ArrayBase<ndarray::ViewRepr<&f32>, ndarray::prelude::Dim<[usize; 2]>, f32> = grid.slice(s![1..ysize-1,1..xsize-1]);
        let left = grid.slice(s![1..ysize-1,0..xsize-2]);
        let right = grid.slice(s![1..ysize-1,2..xsize]);
        let up = grid.slice(s![0..ysize-2,1..xsize-1]);
        let down = grid.slice(s![2..ysize,1..xsize-1]);
        (center,left,right,up,down)
     }
    fn neighbours_center_mut(grid:&mut nd<f32>,xsize: usize,ysize: usize)->
        ArrayViewMut2<'_, f32>
    {
        let mut_center: ndarray::prelude::ArrayBase<ndarray::ViewRepr<&mut f32>, ndarray::prelude::Dim<[usize; 2]>, f32> = grid.slice_mut(s![1..ysize-1,1..xsize-1]);
        mut_center
    }
    fn cfd_step(&mut self,xsize:usize,ysize:usize){
        //self.temperatures[(190,100)] = 393.0;
        let (pc, pl, pr, pu, pd) = Self::neighbours_view(&self.pressure, xsize, ysize);
        let (dc, dl, dr, du, dd) = Self::neighbours_view(&self.density, xsize, ysize);
        let (vxc, vxl, vxr, vxu, vxd) = Self::neighbours_view(&self.vx, xsize, ysize);
        let (vyc, vyl, vyr, vyu, vyd) = Self::neighbours_view(&self.vy, xsize, ysize);
        let mut ndc = Self::neighbours_center_mut(&mut self.next_density, xsize, ysize);
        let mut nvxc =
        Self::neighbours_center_mut(&mut self.next_vx, xsize, ysize);
        let mut nvyc =
        Self::neighbours_center_mut(&mut self.next_vy, xsize, ysize);
        let mut npc = Self::neighbours_center_mut(&mut self.next_pressure, xsize, ysize);
        let (tc,tl,tr,tu,td) = Self::neighbours_view(&self.temperatures, xsize, ysize);
        let conductivity:f32 = 0.1;
        let dx:f32 = 1.0;
        let dy:f32 = 1.0;
        let viscosity = 0.9;
        let adiabatic_index:f32 = 1.4;
        let r_constant:f32 = 287.0;
        let gravity:f32 = -9.810;
        let speed_of_sound_sq = adiabatic_index*(&pc/&dc);
        let max_sound_speed = speed_of_sound_sq.powf(0.5)
            .iter()
            .fold(0.0f32, |max, &val| val.max(max));
        let fluid_speed = &vxc.mapv(|v| v.abs()) + &vyc.mapv(|v| v.abs());
        let max_fluid_speed = fluid_speed
            .iter()
            .fold(0.0f32, |max, &val| val.max(max));
        let max_speed = max_fluid_speed + max_sound_speed;
        let cfl = 0.3;
        let dt = if max_speed > 0.0 {
            cfl * (dx.min(dy) / max_speed)
        } else {
            1e-17
        };
        let mut temporary_array = self.next_temps.slice_mut(s![1..ysize-1,1..xsize-1]);
        Zip::from(&mut temporary_array)
        .and(&tc)
        .and(&tu)
        .and(&td)
        .and(&tl)
        .and(&tr)
        .par_for_each(|next_val, &center, &top, &bottom, &left, &right| {
            let laplacian = top + bottom + left + right - (4.0 * center);
            *next_val = center + (conductivity * laplacian*dt);
        });
        let next_pressure = r_constant*(&dc*&tc);
        npc.assign(&next_pressure);
        let mut upwind_dif_x_x = nd::zeros(vxc.raw_dim());
        Zip::from(&mut upwind_dif_x_x)
        .and(&vxc)
        .and(&vxr)
        .and(&vxl)
        .par_for_each(|udxx, &xc,&xr,&xl| {
            *udxx = if xc > 0.0{
                (xc - xl)/dx
            }
            else{
                (xr - xc)/dx
            }
        });
        let adv_x = upwind_dif_x_x.clone();
        let mut upwind_dif_y_x = nd::zeros(vxc.raw_dim());
        Zip::from(&mut upwind_dif_y_x)
        .and(&vyc)
        .and(&vxc)
        .and(&vxu)
        .and(&vxd)
        .par_for_each(|udyx,&yc,&xc,&xu,&xd|{
            *udyx = if yc > 0.0{
                (xc - xu)/dy
            }
            else{
                (xd - xc)/dy 
                    }
        });
        nvxc.assign(
            &(&vxc
                - (dt*&vxc*&upwind_dif_x_x)
                - (dt*&vyc*&upwind_dif_y_x)
                +dt*(viscosity*
                (((&vxr + &vxl-(2.0*&vxc))/(dx.powf(2.0)))
                +((&vxu+&vxd)- (2.0*&vxc))/(dy.powf(2.0))))
                -dt * (&pr - &pl) / (2.0 * dx * &dc))
        );
        let mut upwind_dif_x_y = nd::zeros(vxc.raw_dim());
        Zip::from(&mut upwind_dif_x_y)
        .and(&vxc)
        .and(&vyc)
        .and(&vyr)
        .and(&vyl)
        .par_for_each(|udxy, &xc,&yc,&yr,&yl| {
            *udxy = if xc > 0.0{
                (yc - yl)/dx
            }
            else{
                (yr - yc)/dx
            }
        });
        let mut upwind_dif_y_y = nd::zeros(vxc.raw_dim());
        Zip::from(&mut upwind_dif_y_y)
        .and(&vyc)
        .and(&vyu)
        .and(&vyd)
        .par_for_each(|udyy, &yc,&yu,&yd| {
            *udyy = if yc > 0.0{
                (yc - yu)/dy
            }
            else{
                (yd - yc)/dy
            }
        });
        let adv_y = upwind_dif_y_y.clone();
        nvyc.assign(
            &(&vyc
                - (dt*&vxc*&upwind_dif_x_y)
                - (dt*&vyc*&upwind_dif_y_y)
                - dt * (&pd - &pu) / (2.0 * dy * &dc)
                +dt*(viscosity*((((&vyr+&vyl)-2.0*&vyc)/(dx.powf(2.0))) 
                + (((&vyu+&vyd)-2.0*&vyc)/(dy.powf(2.0)))))
                + (gravity * dt))
            );
        let mut next_dc_t_h = nd::zeros(dc.raw_dim());
        Zip::from(&mut next_dc_t_h)
        .and(&dc)
        .and(&dr)
        .and(&dl)
        .par_for_each(|ndcth,&dc,dr,dl|{
            *ndcth = if dc > 0.0{
                (dc - dl)/dx
            }
                    else{
                (dr - dc)/dx
                    }
        });
        let mut next_dc_t_v = nd::zeros(dc.raw_dim());
        Zip::from(&mut next_dc_t_v)
        .and(&dc)
        .and(&du)
        .and(&dd)
        .par_for_each(|ndctv,&dc,du,dd|{
            *ndctv = if dc >0.0{
                (dc - du)/dy
                }
                    else{
                (dd - du)/dy
                    }
        });
        ndc.assign(
            &(&dc - dt * (&dc * (adv_x + adv_y) + &vxc * next_dc_t_h + &vyc * next_dc_t_v))
        );
        self.next_density.par_mapv_inplace(|d| d.max(0.1));
        for x in 0..xsize{
            self.next_vx[(1,x)] = self.next_vx[(2,x)];
            self.next_vx[(ysize-1,x)] = self.next_vx[(ysize-2,x)]
        }
        for y in 0..ysize{
            self.next_vx[(y,1)] = self.next_vx[(y,2)];
            self.next_vx[(y,xsize-1)] = self.next_vx[(y,xsize-2)];
        }
        for x in 0..xsize{
            self.next_vy[(1,x)] = self.next_vy[(2,x)];
            self.next_vy[(ysize-1,x)] = self.next_vy[(ysize-2,x)]
        }
        for y in 0..ysize{
            self.next_vy[(y,1)] = self.next_vy[(y,2)];
            self.next_vy[(y,xsize-1)] = self.next_vy[(y,xsize-2)];
        }
        for x in 0..xsize{
            self.next_pressure[(1,x)] = self.next_pressure[(2,x)];
            self.next_pressure[(ysize-1,x)] = self.next_pressure[(ysize-2,x)]
        }
        for y in 0..ysize{
            self.next_pressure[(y,1)] = self.next_pressure[(y,2)];
            self.next_pressure[(y,xsize-1)] = self.next_pressure[(y,xsize-2)];
        }
        for x in 0..xsize{
            self.next_density[(1,x)] = self.next_density[(2,x)];
            self.next_density[(ysize-1,x)] = self.next_density[(ysize-2,x)]
        }
        for y in 0..ysize{
            self.next_density[(y,1)] = self.next_density[(y,2)];
            self.next_density[(y,xsize-1)] = self.next_density[(y,xsize-2)];
        }
        for x in 0..xsize{
            self.next_temps[(1,x)] = self.next_temps[(2,x)];
            self.next_temps[(ysize-1,x)] = self.next_temps[(ysize-2,x)]
    
        }
        for y in 0..ysize{
            self.next_temps[(y,1)] = self.next_temps[(y,2)];
            self.next_temps[(y,xsize-1)] = self.next_temps[(y,xsize-2)];
       }
       let max_p_grad = (-dt * (&pr - &pl) / (2.0 * dx * &dc)).iter().fold(0.0f32, |m, &v| v.abs().max(m));
       println!("max p grad is {:?}",max_p_grad);
       swap(&mut self.next_vx,&mut self.vx);
       swap(&mut self.next_vy,&mut self.vy);
       swap(&mut self.next_pressure,&mut self.pressure);
       swap(&mut self.next_density, &mut self.density);
       swap(&mut self.next_temps, &mut self.temperatures);
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
            min_temp: 25.0,
            max_temp: 500.0,
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
    let xsize = 683;
    let ysize = 384;
    let max_steps:i32 = 100000;
    let steps_per_frame = 1;
    let mut current_steps:i32 = 0;
    let mut sim = Mathpart {
        temperatures: nd::default((ysize, xsize)),
        next_temps: nd::default((ysize, xsize)),
        vx:nd::default((ysize, xsize)),
        vy:nd::default((ysize, xsize)),
        density:nd::default((ysize, xsize)),
        pressure:nd::default((ysize, xsize)),
        next_vx:nd::default((ysize, xsize)),
        next_vy:nd::default((ysize, xsize)),
        next_density:nd::default((ysize, xsize)),
        next_pressure:nd::default((ysize, xsize))
    };
        sim.thermal(xsize,ysize);
    let mut viewer = ThermalViewer::new(xsize, ysize, minifb::Scale::X2,);
    while viewer.is_open() {
        if current_steps < max_steps {
            for _ in 0..steps_per_frame {
                sim.cfd_step(xsize, ysize);
                current_steps += 1;
                if current_steps >= max_steps {
                    break;
                }
            }
            // Render to screen once per batch
            viewer.draw(&(&sim.pressure*0.009));
        } else {
            viewer.window.update();
        }
        }
    }   
