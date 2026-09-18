use crate::domain::document::model::DocumentNode;

pub trait Renderer {
    /// Takes a JSON DocumentNode and returns an intermediate string (e.g. HTML or Markdown)
    fn render(&self, doc: &DocumentNode) -> Result<String, String>;
}

/// The orchestrator for converting a JSON AST into a final format.
pub struct RendererPipeline {
    renderers: Vec<Box<dyn Renderer>>,
}

impl RendererPipeline {
    pub fn new() -> Self {
        Self {
            renderers: Vec::new(),
        }
    }

    pub fn add_renderer(&mut self, renderer: Box<dyn Renderer>) {
        self.renderers.push(renderer);
    }

    pub fn execute(&self, doc: &DocumentNode) -> Result<String, String> {
        // In a real pipeline, the output of one renderer might be the input to another,
        // or a specific renderer might handle the whole AST conversion to HTML.
        // For architectural scaffolding, we mock the pipeline execution.
        let mut final_output = String::new();
        for renderer in &self.renderers {
            final_output = renderer.render(doc)?;
        }
        Ok(final_output)
    }
}

pub struct HtmlRenderer;
impl Renderer for HtmlRenderer {
    fn render(&self, doc: &DocumentNode) -> Result<String, String> {
        // Mock AST to HTML conversion
        if doc.r#type == "doc" {
            return Ok("<div class='neocards-doc'>Rendered Document</div>".to_string());
        }
        Ok(String::new())
    }
}