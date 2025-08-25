#!/usr/bin/env python3
"""
SQL Schema Documentation Generator

This tool analyzes SQL files to generate comprehensive schema documentation
with table relationships, foreign keys, and data flow diagrams.
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class Column:
    """Represents a database column."""
    name: str
    data_type: str
    is_nullable: bool
    default_value: Optional[str]
    auto_increment: bool
    comment: str
    constraints: List[str]


@dataclass
class Index:
    """Represents a database index."""
    name: str
    columns: List[str]
    is_unique: bool
    is_primary: bool
    index_type: str


@dataclass
class ForeignKey:
    """Represents a foreign key relationship."""
    name: str
    column: str
    referenced_table: str
    referenced_column: str
    on_delete: str
    on_update: str


@dataclass
class Table:
    """Represents a database table."""
    name: str
    source_file: str
    engine: str
    charset: str
    comment: str
    columns: List[Column]
    indexes: List[Index]
    foreign_keys: List[ForeignKey]
    estimated_rows: Optional[int] = None


@dataclass
class DatabaseSchema:
    """Represents the complete database schema."""
    tables: Dict[str, Table]
    relationships: List[Tuple[str, str, str]]  # (from_table, to_table, relationship_type)
    views: Dict[str, str]
    procedures: Dict[str, str]


class SQLSchemaGenerator:
    """Generates comprehensive SQL schema documentation."""
    
    def __init__(self, sql_dir: str = "sql", output_dir: str = "documentation/sql_schema"):
        self.sql_dir = Path(sql_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.schema = DatabaseSchema(
            tables={},
            relationships=[],
            views={},
            procedures={}
        )
    
    def analyze_sql_files(self) -> None:
        """Analyze all SQL files in the directory."""
        print("🗄️ Analyzing SQL schema files...")
        
        if not self.sql_dir.exists():
            print("⚠️ SQL directory not found")
            return
        
        # Process all SQL files
        for sql_file in self.sql_dir.glob("*.sql"):
            print(f"📄 Processing {sql_file.name}")
            self._analyze_sql_file(sql_file)
        
        # Build relationships after all tables are processed
        self._build_relationships()
        
        print(f"📊 Found {len(self.schema.tables)} tables, {len(self.schema.relationships)} relationships")
    
    def _analyze_sql_file(self, file_path: Path) -> None:
        """Analyze a single SQL file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Remove SQL comments and normalize
            content = self._clean_sql_content(content)
            
            # Find CREATE TABLE statements
            self._extract_tables(content, str(file_path))
            
            # Find CREATE VIEW statements
            self._extract_views(content, str(file_path))
            
            # Find stored procedures
            self._extract_procedures(content, str(file_path))
            
        except Exception as e:
            print(f"⚠️ Error analyzing {file_path}: {e}")
    
    def _clean_sql_content(self, content: str) -> str:
        """Clean SQL content by removing comments and normalizing."""
        # Remove single-line comments
        content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content)
        
        return content
    
    def _extract_tables(self, content: str, source_file: str) -> None:
        """Extract table definitions from SQL content."""
        # Pattern to match CREATE TABLE statements
        table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:`?)(\w+)(?:`?)\s*\((.*?)\)(?:\s*(ENGINE\s*=\s*\w+))?(?:\s*(DEFAULT\s+CHARSET\s*=\s*\w+))?(?:\s*(COMMENT\s*=\s*[\'"][^\'"]*[\'"]))?'
        
        matches = re.finditer(table_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            table_name = match.group(1)
            table_definition = match.group(2)
            engine = match.group(3) or ""
            charset = match.group(4) or ""
            comment = match.group(5) or ""
            
            # Parse engine
            engine_match = re.search(r'ENGINE\s*=\s*(\w+)', engine, re.IGNORECASE)
            engine_name = engine_match.group(1) if engine_match else "InnoDB"
            
            # Parse charset
            charset_match = re.search(r'DEFAULT\s+CHARSET\s*=\s*(\w+)', charset, re.IGNORECASE)
            charset_name = charset_match.group(1) if charset_match else "utf8"
            
            # Parse comment
            comment_match = re.search(r'COMMENT\s*=\s*[\'"]([^\'"]*)[\'"]', comment, re.IGNORECASE)
            comment_text = comment_match.group(1) if comment_match else ""
            
            # Parse table definition
            columns, indexes, foreign_keys = self._parse_table_definition(table_definition)
            
            table = Table(
                name=table_name,
                source_file=source_file,
                engine=engine_name,
                charset=charset_name,
                comment=comment_text,
                columns=columns,
                indexes=indexes,
                foreign_keys=foreign_keys
            )
            
            self.schema.tables[table_name] = table
    
    def _parse_table_definition(self, definition: str) -> Tuple[List[Column], List[Index], List[ForeignKey]]:
        """Parse the table definition to extract columns, indexes, and foreign keys."""
        columns = []
        indexes = []
        foreign_keys = []
        
        # Split definition into individual elements
        elements = self._split_table_elements(definition)
        
        for element in elements:
            element = element.strip()
            if not element:
                continue
            
            # Check if it's a constraint
            if self._is_constraint(element):
                constraint_type = self._get_constraint_type(element)
                
                if constraint_type == "PRIMARY KEY":
                    index = self._parse_primary_key(element)
                    if index:
                        indexes.append(index)
                
                elif constraint_type == "FOREIGN KEY":
                    fk = self._parse_foreign_key(element)
                    if fk:
                        foreign_keys.append(fk)
                
                elif constraint_type in ["KEY", "INDEX", "UNIQUE"]:
                    index = self._parse_index(element)
                    if index:
                        indexes.append(index)
            
            else:
                # It's a column definition
                column = self._parse_column(element)
                if column:
                    columns.append(column)
        
        return columns, indexes, foreign_keys
    
    def _split_table_elements(self, definition: str) -> List[str]:
        """Split table definition into individual elements (columns, constraints)."""
        elements = []
        current_element = ""
        paren_count = 0
        in_string = False
        string_char = None
        
        for char in definition:
            if char in ["'", '"'] and not in_string:
                in_string = True
                string_char = char
            elif char == string_char and in_string:
                in_string = False
                string_char = None
            elif char == '(' and not in_string:
                paren_count += 1
            elif char == ')' and not in_string:
                paren_count -= 1
            elif char == ',' and paren_count == 0 and not in_string:
                elements.append(current_element.strip())
                current_element = ""
                continue
            
            current_element += char
        
        if current_element.strip():
            elements.append(current_element.strip())
        
        return elements
    
    def _is_constraint(self, element: str) -> bool:
        """Check if element is a constraint definition."""
        constraint_keywords = ['PRIMARY KEY', 'FOREIGN KEY', 'KEY', 'INDEX', 'UNIQUE', 'CONSTRAINT']
        element_upper = element.upper()
        return any(keyword in element_upper for keyword in constraint_keywords)
    
    def _get_constraint_type(self, element: str) -> str:
        """Get the type of constraint."""
        element_upper = element.upper()
        if 'PRIMARY KEY' in element_upper:
            return "PRIMARY KEY"
        elif 'FOREIGN KEY' in element_upper:
            return "FOREIGN KEY"
        elif 'UNIQUE' in element_upper:
            return "UNIQUE"
        elif 'KEY' in element_upper or 'INDEX' in element_upper:
            return "KEY"
        return "UNKNOWN"
    
    def _parse_column(self, element: str) -> Optional[Column]:
        """Parse a column definition."""
        try:
            # Basic pattern: column_name data_type [constraints]
            match = re.match(r'(?:`?)(\w+)(?:`?)\s+([^\s,]+)(.*)$', element.strip())
            if not match:
                return None
            
            column_name = match.group(1)
            data_type = match.group(2)
            constraints_str = match.group(3).strip()
            
            # Parse constraints
            is_nullable = 'NOT NULL' not in constraints_str.upper()
            auto_increment = 'AUTO_INCREMENT' in constraints_str.upper()
            
            # Extract default value
            default_match = re.search(r'DEFAULT\s+([^\s,]+)', constraints_str, re.IGNORECASE)
            default_value = default_match.group(1) if default_match else None
            
            # Extract comment
            comment_match = re.search(r'COMMENT\s+[\'"]([^\'"]*)[\'"]', constraints_str, re.IGNORECASE)
            comment = comment_match.group(1) if comment_match else ""
            
            # Extract other constraints
            constraints = []
            if 'NOT NULL' in constraints_str.upper():
                constraints.append('NOT NULL')
            if 'AUTO_INCREMENT' in constraints_str.upper():
                constraints.append('AUTO_INCREMENT')
            if 'UNSIGNED' in constraints_str.upper():
                constraints.append('UNSIGNED')
            
            return Column(
                name=column_name,
                data_type=data_type,
                is_nullable=is_nullable,
                default_value=default_value,
                auto_increment=auto_increment,
                comment=comment,
                constraints=constraints
            )
        
        except Exception:
            return None
    
    def _parse_primary_key(self, element: str) -> Optional[Index]:
        """Parse a primary key constraint."""
        try:
            # Extract column names from PRIMARY KEY (col1, col2, ...)
            match = re.search(r'PRIMARY\s+KEY\s*\(([^)]+)\)', element, re.IGNORECASE)
            if not match:
                return None
            
            columns_str = match.group(1)
            columns = [col.strip().strip('`') for col in columns_str.split(',')]
            
            return Index(
                name="PRIMARY",
                columns=columns,
                is_unique=True,
                is_primary=True,
                index_type="BTREE"
            )
        
        except Exception:
            return None
    
    def _parse_foreign_key(self, element: str) -> Optional[ForeignKey]:
        """Parse a foreign key constraint."""
        try:
            # Pattern: FOREIGN KEY (column) REFERENCES table(column) [ON DELETE ...] [ON UPDATE ...]
            pattern = r'FOREIGN\s+KEY\s*\(([^)]+)\)\s+REFERENCES\s+(\w+)\s*\(([^)]+)\)(?:\s+ON\s+DELETE\s+(\w+))?(?:\s+ON\s+UPDATE\s+(\w+))?'
            match = re.search(pattern, element, re.IGNORECASE)
            
            if not match:
                return None
            
            column = match.group(1).strip().strip('`')
            referenced_table = match.group(2)
            referenced_column = match.group(3).strip().strip('`')
            on_delete = match.group(4) or "RESTRICT"
            on_update = match.group(5) or "RESTRICT"
            
            return ForeignKey(
                name=f"fk_{column}_{referenced_table}",
                column=column,
                referenced_table=referenced_table,
                referenced_column=referenced_column,
                on_delete=on_delete,
                on_update=on_update
            )
        
        except Exception:
            return None
    
    def _parse_index(self, element: str) -> Optional[Index]:
        """Parse an index definition."""
        try:
            # Pattern: [UNIQUE] KEY index_name (columns) or INDEX index_name (columns)
            pattern = r'(?:(UNIQUE)\s+)?(?:KEY|INDEX)\s+(?:(\w+)\s+)?\(([^)]+)\)'
            match = re.search(pattern, element, re.IGNORECASE)
            
            if not match:
                return None
            
            is_unique = match.group(1) is not None
            index_name = match.group(2) or "idx_unnamed"
            columns_str = match.group(3)
            
            columns = [col.strip().strip('`') for col in columns_str.split(',')]
            
            return Index(
                name=index_name,
                columns=columns,
                is_unique=is_unique,
                is_primary=False,
                index_type="BTREE"
            )
        
        except Exception:
            return None
    
    def _extract_views(self, content: str, source_file: str) -> None:
        """Extract view definitions."""
        view_pattern = r'CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+(\w+)\s+AS\s+(.*?)(?=CREATE|$)'
        matches = re.finditer(view_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            view_name = match.group(1)
            view_definition = match.group(2).strip()
            self.schema.views[view_name] = view_definition
    
    def _extract_procedures(self, content: str, source_file: str) -> None:
        """Extract stored procedure definitions."""
        proc_pattern = r'CREATE\s+(?:DEFINER.*?\s+)?PROCEDURE\s+(\w+)\s*\((.*?)\)\s+(.*?)(?=CREATE|$)'
        matches = re.finditer(proc_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            proc_name = match.group(1)
            proc_params = match.group(2).strip()
            proc_body = match.group(3).strip()
            self.schema.procedures[proc_name] = f"({proc_params}) {proc_body}"
    
    def _build_relationships(self) -> None:
        """Build table relationships based on foreign keys."""
        print("🔗 Building table relationships...")
        
        for table_name, table in self.schema.tables.items():
            for fk in table.foreign_keys:
                relationship = (table_name, fk.referenced_table, "foreign_key")
                self.schema.relationships.append(relationship)
    
    def generate_documentation(self) -> None:
        """Generate comprehensive SQL schema documentation."""
        print("📝 Generating SQL schema documentation...")
        
        self._generate_main_index()
        self._generate_table_documentation()
        self._generate_relationship_diagram()
        self._generate_data_dictionary()
        self._generate_json_schema()
        
        print(f"📚 SQL schema documentation generated in: {self.output_dir}")
    
    def _generate_main_index(self) -> None:
        """Generate the main schema index."""
        index_path = self.output_dir / "index.md"
        
        with open(index_path, 'w') as f:
            f.write("# LandSandBoat Database Schema Documentation\n\n")
            f.write("Comprehensive documentation for the database schema.\n\n")
            
            # Statistics
            f.write("## Database Statistics\n\n")
            f.write(f"- **Tables**: {len(self.schema.tables)}\n")
            f.write(f"- **Views**: {len(self.schema.views)}\n")
            f.write(f"- **Stored Procedures**: {len(self.schema.procedures)}\n")
            f.write(f"- **Relationships**: {len(self.schema.relationships)}\n\n")
            
            # Table categories
            table_categories = self._categorize_tables()
            f.write("## Table Categories\n\n")
            for category, tables in sorted(table_categories.items()):
                f.write(f"### {category.title()} ({len(tables)} tables)\n\n")
                for table_name in sorted(tables):
                    table = self.schema.tables[table_name]
                    f.write(f"- [{table_name}](tables/{table_name}.md)")
                    if table.comment:
                        f.write(f" - {table.comment}")
                    f.write("\n")
                f.write("\n")
            
            f.write("## Additional Documentation\n\n")
            f.write("- [Relationship Diagram](relationships.md)\n")
            f.write("- [Data Dictionary](data_dictionary.md)\n")
            f.write("- [JSON Schema](json/schema.json)\n\n")
    
    def _categorize_tables(self) -> Dict[str, List[str]]:
        """Categorize tables based on naming patterns."""
        categories = {
            'characters': [],
            'accounts': [],
            'items': [],
            'monsters': [],
            'zones': [],
            'system': [],
            'logs': [],
            'other': []
        }
        
        for table_name in self.schema.tables.keys():
            if table_name.startswith('char_'):
                categories['characters'].append(table_name)
            elif table_name.startswith('account'):
                categories['accounts'].append(table_name)
            elif table_name.startswith('item_'):
                categories['items'].append(table_name)
            elif table_name.startswith('mob_'):
                categories['monsters'].append(table_name)
            elif table_name.startswith('zone_') or 'zone' in table_name:
                categories['zones'].append(table_name)
            elif table_name.startswith('audit_') or table_name.endswith('_log'):
                categories['logs'].append(table_name)
            elif table_name in ['server_variables', 'conquest_system', 'transport']:
                categories['system'].append(table_name)
            else:
                categories['other'].append(table_name)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _generate_table_documentation(self) -> None:
        """Generate individual table documentation."""
        tables_dir = self.output_dir / "tables"
        tables_dir.mkdir(exist_ok=True)
        
        for table_name, table in self.schema.tables.items():
            table_path = tables_dir / f"{table_name}.md"
            
            with open(table_path, 'w') as f:
                f.write(f"# Table: {table_name}\n\n")
                
                if table.comment:
                    f.write(f"**Description**: {table.comment}\n\n")
                
                f.write(f"**Source File**: `{table.source_file}`\n")
                f.write(f"**Engine**: {table.engine}\n")
                f.write(f"**Charset**: {table.charset}\n\n")
                
                # Columns
                f.write("## Columns\n\n")
                f.write("| Column | Type | Nullable | Default | Auto Inc | Constraints | Comment |\n")
                f.write("|--------|------|----------|---------|----------|-------------|--------|\n")
                
                for col in table.columns:
                    nullable = "Yes" if col.is_nullable else "No"
                    auto_inc = "Yes" if col.auto_increment else "No"
                    default = col.default_value or ""
                    constraints = ", ".join(col.constraints)
                    comment = col.comment or ""
                    
                    f.write(f"| {col.name} | {col.data_type} | {nullable} | {default} | {auto_inc} | {constraints} | {comment} |\n")
                
                # Indexes
                if table.indexes:
                    f.write("\n## Indexes\n\n")
                    f.write("| Name | Columns | Type | Unique | Primary |\n")
                    f.write("|------|---------|------|--------|--------|\n")
                    
                    for idx in table.indexes:
                        columns = ", ".join(idx.columns)
                        unique = "Yes" if idx.is_unique else "No"
                        primary = "Yes" if idx.is_primary else "No"
                        f.write(f"| {idx.name} | {columns} | {idx.index_type} | {unique} | {primary} |\n")
                
                # Foreign Keys
                if table.foreign_keys:
                    f.write("\n## Foreign Keys\n\n")
                    f.write("| Column | References | On Delete | On Update |\n")
                    f.write("|--------|------------|-----------|----------|\n")
                    
                    for fk in table.foreign_keys:
                        reference = f"{fk.referenced_table}.{fk.referenced_column}"
                        f.write(f"| {fk.column} | {reference} | {fk.on_delete} | {fk.on_update} |\n")
                
                # Relationships
                related_tables = self._find_related_tables(table_name)
                if related_tables:
                    f.write("\n## Related Tables\n\n")
                    for rel_table, rel_type in related_tables:
                        f.write(f"- [{rel_table}]({rel_table}.md) ({rel_type})\n")
    
    def _find_related_tables(self, table_name: str) -> List[Tuple[str, str]]:
        """Find tables related to the given table."""
        related = []
        
        for from_table, to_table, rel_type in self.schema.relationships:
            if from_table == table_name:
                related.append((to_table, f"references {to_table}"))
            elif to_table == table_name:
                related.append((from_table, f"referenced by {from_table}"))
        
        return related
    
    def _generate_relationship_diagram(self) -> None:
        """Generate relationship diagram documentation."""
        rel_path = self.output_dir / "relationships.md"
        
        with open(rel_path, 'w') as f:
            f.write("# Database Relationships\n\n")
            f.write("This page documents the relationships between database tables.\n\n")
            
            # Group relationships by from_table
            by_table = {}
            for from_table, to_table, rel_type in self.schema.relationships:
                if from_table not in by_table:
                    by_table[from_table] = []
                by_table[from_table].append((to_table, rel_type))
            
            f.write("## Foreign Key Relationships\n\n")
            for from_table, relationships in sorted(by_table.items()):
                f.write(f"### {from_table}\n\n")
                for to_table, rel_type in relationships:
                    f.write(f"- **{to_table}** ({rel_type})\n")
                f.write("\n")
    
    def _generate_data_dictionary(self) -> None:
        """Generate a comprehensive data dictionary."""
        dict_path = self.output_dir / "data_dictionary.md"
        
        with open(dict_path, 'w') as f:
            f.write("# Data Dictionary\n\n")
            f.write("Comprehensive listing of all database objects.\n\n")
            
            # Tables summary
            f.write("## Tables Summary\n\n")
            f.write("| Table | Columns | Indexes | Foreign Keys | Comment |\n")
            f.write("|-------|---------|---------|--------------|--------|\n")
            
            for table_name, table in sorted(self.schema.tables.items()):
                col_count = len(table.columns)
                idx_count = len(table.indexes)
                fk_count = len(table.foreign_keys)
                comment = table.comment or ""
                
                f.write(f"| [{table_name}](tables/{table_name}.md) | {col_count} | {idx_count} | {fk_count} | {comment} |\n")
            
            # Views
            if self.schema.views:
                f.write("\n## Views\n\n")
                f.write("| View | Definition |\n")
                f.write("|------|------------|\n")
                
                for view_name, definition in sorted(self.schema.views.items()):
                    # Truncate long definitions
                    short_def = definition[:100] + "..." if len(definition) > 100 else definition
                    f.write(f"| {view_name} | `{short_def}` |\n")
            
            # Stored Procedures
            if self.schema.procedures:
                f.write("\n## Stored Procedures\n\n")
                f.write("| Procedure | Definition |\n")
                f.write("|-----------|------------|\n")
                
                for proc_name, definition in sorted(self.schema.procedures.items()):
                    short_def = definition[:100] + "..." if len(definition) > 100 else definition
                    f.write(f"| {proc_name} | `{short_def}` |\n")
    
    def _generate_json_schema(self) -> None:
        """Generate JSON schema representation."""
        json_dir = self.output_dir / "json"
        json_dir.mkdir(exist_ok=True)
        
        # Convert schema to JSON-serializable format
        schema_data = {
            'tables': {name: asdict(table) for name, table in self.schema.tables.items()},
            'relationships': self.schema.relationships,
            'views': self.schema.views,
            'procedures': self.schema.procedures
        }
        
        with open(json_dir / "schema.json", 'w') as f:
            json.dump(schema_data, f, indent=2)
    
    def generate(self) -> None:
        """Main method to generate SQL schema documentation."""
        self.analyze_sql_files()
        self.generate_documentation()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate SQL schema documentation")
    parser.add_argument("--sql-dir", default="sql", help="SQL directory to analyze")
    parser.add_argument("--output-dir", default="documentation/sql_schema", help="Output directory")
    
    args = parser.parse_args()
    
    generator = SQLSchemaGenerator(args.sql_dir, args.output_dir)
    generator.generate()


if __name__ == "__main__":
    main()