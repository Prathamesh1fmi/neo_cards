use crate::domain::document::model::DocumentNode;

pub struct ValidationEngine;

impl ValidationEngine {
    pub fn validate_document(doc: &DocumentNode) -> Result<(), String> {
        if doc.r#type != "doc" {
            return Err("Invalid root node: must be 'doc'".to_string());
        }
        Self::validate_node_recursive(doc)?;
        Ok(())
    }

    fn validate_node_recursive(node: &DocumentNode) -> Result<(), String> {
        // Mock validation: check for unsupported node types or broken media references
        if node.r#type == "unknown_plugin_node" {
            return Err("Unsupported node type detected".to_string());
        }

        if let Some(children) = &node.content {
            for child in children {
                Self::validate_node_recursive(child)?;
            }
        }
        Ok(())
    }
}