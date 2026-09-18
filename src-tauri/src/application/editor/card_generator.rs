use std::collections::HashMap;
use handlebars::Handlebars;
use crate::domain::editor::note_type::{NoteType, CardTemplate};
use crate::domain::card::Card;

pub struct GeneratedPreview {
    pub template_id: String,
    pub template_name: String,
    pub front_compiled: String,
    pub back_compiled: String,
}

pub struct CardGenerator<'a> {
    registry: Handlebars<'a>,
}

impl<'a> CardGenerator<'a> {
    pub fn new() -> Self {
        let mut registry = Handlebars::new();
        // Disable HTML escaping to allow rich text fields to render natively
        registry.register_escape_fn(handlebars::no_escape);
        Self { registry }
    }

    /// Evaluates templates against the provided fields map. 
    /// Returns the compiled HTML previews. React will render these.
    pub fn generate_preview(&self, note_type: &NoteType, fields: &HashMap<String, String>) -> Result<Vec<GeneratedPreview>, String> {
        let mut previews = Vec::new();

        for template in &note_type.templates {
            // Check conditional: Anki standard is if Front is empty, do not generate card.
            // A robust implementation would use AST parsing, but for Milestone 3, we leverage Handlebars.
            let front_compiled = self.registry.render_template(&template.front_html, fields).map_err(|e| e.to_string())?;
            let back_compiled = self.registry.render_template(&template.back_html, fields).map_err(|e| e.to_string())?;

            if !front_compiled.trim().is_empty() {
                previews.push(GeneratedPreview {
                    template_id: template.id.clone(),
                    template_name: template.name.clone(),
                    front_compiled,
                    back_compiled,
                });
            }
        }

        Ok(previews)
    }
}