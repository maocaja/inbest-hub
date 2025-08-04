import httpx
from typing import List, Dict, Any, Optional
from loguru import logger
from config import Config
from schemas.schemas import ProjectInfo, SearchRequest, SearchResponse

class SearchService:
    def __init__(self):
        self.embedding_service_url = Config.EMBEDDING_SERVICE_URL
        self.projects_service_url = Config.PROJECTS_SERVICE_URL
        self.timeout = Config.REQUEST_TIMEOUT
    
    async def search_projects(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Busca proyectos usando el embedding service y aplica filtros adicionales"""
        try:
            # Construir query de búsqueda
            query = self._build_search_query(filters)
            
            # Buscar en embedding service
            search_results = await self._search_embedding_service(query, filters)
            
            if not search_results:
                return []
            
            # Obtener detalles completos de proyectos
            projects_with_details = await self._get_project_details(search_results)
            
            # Aplicar filtros adicionales
            filtered_projects = self._apply_filters(projects_with_details, filters)
            
            # Ranking inteligente
            ranked_projects = self._rank_projects(filtered_projects, filters)
            
            return ranked_projects
            
        except Exception as e:
            logger.error(f"Error en búsqueda de proyectos: {e}")
            return []
    
    def _build_search_query(self, filters: Dict[str, Any]) -> str:
        """Construye query de búsqueda basado en filtros"""
        query_parts = []
        
        if filters.get("location"):
            query_parts.append(f"ubicado en {filters['location']}")
        
        if filters.get("property_type"):
            query_parts.append(f"tipo {filters['property_type']}")
        
        if filters.get("amenities"):
            amenities = filters["amenities"]
            if isinstance(amenities, list):
                query_parts.append(f"con amenities: {', '.join(amenities)}")
            else:
                query_parts.append(f"con {amenities}")
        
        if filters.get("price_range"):
            price_range = filters["price_range"]
            if isinstance(price_range, dict):
                min_price = price_range.get("min", 0)
                max_price = price_range.get("max", float('inf'))
                query_parts.append(f"precio entre {min_price} y {max_price}")
        
        if filters.get("query"):
            query_parts.insert(0, filters["query"])
        
        return " ".join(query_parts) if query_parts else "proyectos inmobiliarios"
    
    async def _search_embedding_service(self, query: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Busca en el embedding service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.embedding_service_url}/search",
                    json={
                        "query": query,
                        "max_results": Config.SEARCH_MAX_RESULTS,
                        "similarity_threshold": 0.3
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
                else:
                    logger.error(f"Error en embedding service: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error conectando con embedding service: {e}")
            return []
    
    async def _get_project_details(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Obtiene detalles completos de proyectos desde projects service"""
        try:
            project_ids = [result.get("project_id") for result in search_results if result.get("project_id")]
            
            if not project_ids:
                return []
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                projects_with_details = []
                
                for project_id in project_ids:
                    try:
                        response = await client.get(f"{self.projects_service_url}/projects/{project_id}")
                        
                        if response.status_code == 200:
                            project_data = response.json()
                            # Combinar datos de búsqueda con detalles
                            search_result = next((r for r in search_results if r.get("project_id") == project_id), {})
                            project_data["search_score"] = search_result.get("score", 0)
                            project_data["similarity"] = search_result.get("similarity", 0)
                            projects_with_details.append(project_data)
                            
                    except Exception as e:
                        logger.error(f"Error obteniendo detalles del proyecto {project_id}: {e}")
                        continue
                
                return projects_with_details
                
        except Exception as e:
            logger.error(f"Error obteniendo detalles de proyectos: {e}")
            return []
    
    def _apply_filters(self, projects: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aplica filtros adicionales a los proyectos"""
        filtered_projects = projects
        
        # Filtro por precio
        if filters.get("price_range"):
            price_range = filters["price_range"]
            min_price = price_range.get("min", 0)
            max_price = price_range.get("max", float('inf'))
            
            filtered_projects = [
                p for p in filtered_projects
                if self._get_project_price(p) >= min_price and self._get_project_price(p) <= max_price
            ]
        
        # Filtro por amenities
        if filters.get("amenities"):
            required_amenities = filters["amenities"]
            if isinstance(required_amenities, list):
                filtered_projects = [
                    p for p in filtered_projects
                    if all(amenity in self._get_project_amenities(p) for amenity in required_amenities)
                ]
        
        # Filtro por ubicación
        if filters.get("location"):
            location_filter = filters["location"].lower()
            filtered_projects = [
                p for p in filtered_projects
                if location_filter in self._get_project_location(p).lower()
            ]
        
        return filtered_projects
    
    def _rank_projects(self, projects: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ranking inteligente de proyectos basado en múltiples criterios"""
        for project in projects:
            # Score semántico (40%)
            semantic_score = project.get("search_score", 0) * 0.4
            
            # Score de ubicación (25%)
            location_score = self._calculate_location_score(project, filters) * 0.25
            
            # Score de precio (20%)
            price_score = self._calculate_price_score(project, filters) * 0.20
            
            # Score de amenities (10%)
            amenities_score = self._calculate_amenities_score(project, filters) * 0.10
            
            # Score de disponibilidad (5%)
            availability_score = self._calculate_availability_score(project) * 0.05
            
            # Score final
            final_score = semantic_score + location_score + price_score + amenities_score + availability_score
            project["final_score"] = round(final_score, 3)
        
        # Ordenar por score final
        return sorted(projects, key=lambda x: x.get("final_score", 0), reverse=True)
    
    def _get_project_price(self, project: Dict[str, Any]) -> float:
        """Obtiene el precio del proyecto"""
        try:
            price_info = project.get("price_info", {})
            if isinstance(price_info, dict):
                return price_info.get("min_price", 0)
            return 0
        except:
            return 0
    
    def _get_project_amenities(self, project: Dict[str, Any]) -> List[str]:
        """Obtiene las amenities del proyecto"""
        try:
            amenities = project.get("amenities", [])
            if isinstance(amenities, list):
                return amenities
            return []
        except:
            return []
    
    def _get_project_location(self, project: Dict[str, Any]) -> str:
        """Obtiene la ubicación del proyecto"""
        try:
            location = project.get("location", {})
            if isinstance(location, dict):
                return f"{location.get('city', '')} {location.get('department', '')}".strip()
            return str(location)
        except:
            return ""
    
    def _calculate_location_score(self, project: Dict[str, Any], filters: Dict[str, Any]) -> float:
        """Calcula score de ubicación"""
        if not filters.get("location"):
            return 0.5  # Score neutral si no hay filtro de ubicación
        
        project_location = self._get_project_location(project).lower()
        filter_location = filters["location"].lower()
        
        if filter_location in project_location:
            return 1.0
        elif any(word in project_location for word in filter_location.split()):
            return 0.7
        else:
            return 0.3
    
    def _calculate_price_score(self, project: Dict[str, Any], filters: Dict[str, Any]) -> float:
        """Calcula score de precio"""
        if not filters.get("price_range"):
            return 0.5
        
        project_price = self._get_project_price(project)
        price_range = filters["price_range"]
        min_price = price_range.get("min", 0)
        max_price = price_range.get("max", float('inf'))
        
        if min_price <= project_price <= max_price:
            return 1.0
        elif project_price < min_price:
            return 0.3
        else:
            return 0.1
    
    def _calculate_amenities_score(self, project: Dict[str, Any], filters: Dict[str, Any]) -> float:
        """Calcula score de amenities"""
        if not filters.get("amenities"):
            return 0.5
        
        project_amenities = self._get_project_amenities(project)
        required_amenities = filters["amenities"]
        
        if isinstance(required_amenities, list):
            matches = sum(1 for amenity in required_amenities if amenity in project_amenities)
            return min(matches / len(required_amenities), 1.0)
        else:
            return 1.0 if required_amenities in project_amenities else 0.0
    
    def _calculate_availability_score(self, project: Dict[str, Any]) -> float:
        """Calcula score de disponibilidad"""
        try:
            unit_info = project.get("unit_info", {})
            if isinstance(unit_info, dict):
                available_units = unit_info.get("available_units", 0)
                total_units = unit_info.get("total_units", 1)
                
                if total_units > 0:
                    availability_ratio = available_units / total_units
                    return min(availability_ratio, 1.0)
            
            return 0.5  # Score neutral si no hay información
        except:
            return 0.5 