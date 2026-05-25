#[derive(Debug, Clone)]
pub struct RunRng {
    state: u64,
}

impl RunRng {
    pub fn new(seed: u64) -> Self {
        let mut state = seed ^ 0x9e37_79b9_7f4a_7c15;
        if state == 0 {
            state = 0xa5a5_5a5a_d3c7_b911;
        }
        Self { state }
    }

    pub fn next_u32(&mut self) -> u32 {
        self.state = self
            .state
            .wrapping_mul(6_364_136_223_846_793_005)
            .wrapping_add(1_442_695_040_888_963_407);
        (self.state >> 32) as u32
    }

    pub fn next_f32(&mut self) -> f32 {
        const SCALE: f32 = 1.0 / ((1u32 << 24) as f32);
        ((self.next_u32() >> 8) as f32) * SCALE
    }

    pub fn range_f32(&mut self, min: f32, max: f32) -> f32 {
        min + (max - min) * self.next_f32()
    }

    pub fn range_usize(&mut self, upper_exclusive: usize) -> usize {
        if upper_exclusive == 0 {
            0
        } else {
            (self.next_u32() as usize) % upper_exclusive
        }
    }
}
