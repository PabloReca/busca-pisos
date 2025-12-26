let allListings = [];
let currentPage = 1;
let totalPages = 1;
const PAGE_SIZE = 20;

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  loadListings();
  setupEventListeners();
});

function setupEventListeners() {
  // Distance slider
  document.getElementById("filter-distance").addEventListener("input", (e) => {
    document.getElementById("distance-value").textContent =
      e.target.value + " km";
  });

  // Enter to apply filters
  document.querySelectorAll("input, select").forEach((el) => {
    el.addEventListener("keypress", (e) => {
      if (e.key === "Enter") applyFilters();
    });
  });

  // Close modal on outside click
  document.getElementById("modal").addEventListener("click", (e) => {
    if (e.target.id === "modal") closeModal();
  });

  // Close modal with Escape
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });
}

async function loadListings(page = 1) {
  currentPage = page;
  const params = buildFilterParams();
  params.set("page", page);
  params.set("page_size", PAGE_SIZE);

  try {
    const response = await fetch("/api/listings?" + params.toString());
    const data = await response.json();
    allListings = data.listings;
    totalPages = data.pages;
    renderListings(data.listings);
    updateStats(data.total);
    renderPagination();
  } catch (err) {
    console.error("Error loading listings:", err);
    document.getElementById("listings").innerHTML = `
            <div class="col-span-full text-center py-12">
                <p class="text-red-500">Error loading listings</p>
            </div>
        `;
  }
}

function buildFilterParams() {
  const params = new URLSearchParams();

  const type = document.getElementById("filter-type").value;
  const minPrice = document.getElementById("filter-min-price").value;
  const maxPrice = document.getElementById("filter-max-price").value;
  const minRooms = document.getElementById("filter-min-rooms").value;
  const maxRooms = document.getElementById("filter-max-rooms").value;
  const minBathrooms = document.getElementById("filter-min-bathrooms").value;
  const maxBathrooms = document.getElementById("filter-max-bathrooms").value;
  const maxDistance = document.getElementById("filter-distance").value;
  const [sortBy, sortOrder] = document
    .getElementById("filter-sort")
    .value.split("-");

  if (type) params.set("property_type", type);
  if (minPrice) params.set("min_price", minPrice);
  if (maxPrice) params.set("max_price", maxPrice);
  if (minRooms) params.set("min_rooms", minRooms);
  if (maxRooms) params.set("max_rooms", maxRooms);
  if (minBathrooms) params.set("min_bathrooms", minBathrooms);
  if (maxBathrooms) params.set("max_bathrooms", maxBathrooms);
  if (maxDistance && maxDistance < 40) params.set("max_distance", maxDistance);
  params.set("sort_by", sortBy);
  params.set("sort_order", sortOrder);

  return params;
}

function renderListings(listings) {
  const container = document.getElementById("listings");
  const emptyState = document.getElementById("empty-state");

  if (listings.length === 0) {
    container.innerHTML = "";
    emptyState.classList.remove("hidden");
    return;
  }

  emptyState.classList.add("hidden");
  container.innerHTML = listings
    .map((listing, index) => createCard(listing, index))
    .join("");
}

function createCard(listing, index) {
  const images = listing.images || [];
  const firstImage =
    images[0] || "https://via.placeholder.com/400x300?text=Sin+imagen";
  const typeLabel = listing.property_type === "apartment" ? "Piso" : "Casa";
  const typeColor =
    listing.property_type === "apartment"
      ? "bg-blue-100 text-blue-800"
      : "bg-green-100 text-green-800";

  const rooms = listing.type_attributes?.rooms || listing.rooms;
  const bathrooms = listing.type_attributes?.bathrooms || listing.bathrooms;
  const surface = listing.type_attributes?.surface || listing.square_meters;

  return `
        <div class="listing-card bg-white rounded-lg shadow overflow-hidden cursor-pointer hover:shadow-lg"
             onclick="openModal(${index})">
            <div class="relative">
                <img src="${escapeHtml(firstImage)}"
                     alt="${escapeHtml(listing.title)}"
                     class="w-full h-48 object-cover"
                     loading="lazy"
                     onerror="this.src='https://via.placeholder.com/400x300?text=Error'">
                <span class="absolute top-2 left-2 ${typeColor} text-xs font-medium px-2 py-1 rounded">
                    ${typeLabel}
                </span>
                ${
                  images.length > 1
                    ? `
                    <span class="absolute top-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded">
                        ${images.length}
                    </span>
                `
                    : ""
                }
            </div>
            <div class="p-4">
                <h3 class="font-semibold text-gray-800 line-clamp-1 mb-2">${escapeHtml(listing.title)}</h3>
                <p class="text-2xl font-bold text-blue-600 mb-2">
                    ${listing.price}€<span class="text-sm font-normal text-gray-500">/mes</span>
                </p>
                <div class="flex flex-wrap gap-2 text-sm text-gray-600">
                    ${rooms ? `<span>${rooms} hab</span>` : ""}
                    ${bathrooms ? `<span>${bathrooms} banos</span>` : ""}
                    ${surface ? `<span>${surface}m2</span>` : ""}
                    ${listing.distance_km ? `<span>${listing.distance_km}km</span>` : ""}
                </div>
            </div>
        </div>
    `;
}

function renderPagination() {
  const container = document.getElementById("pagination");
  if (!container) return;

  if (totalPages <= 1) {
    container.innerHTML = "";
    return;
  }

  let html = '<div class="flex justify-center items-center gap-2 mt-6">';

  // Previous button
  html += `
        <button onclick="goToPage(${currentPage - 1})"
                ${currentPage === 1 ? "disabled" : ""}
                class="px-3 py-2 rounded ${currentPage === 1 ? "bg-gray-200 text-gray-400 cursor-not-allowed" : "bg-blue-600 text-white hover:bg-blue-700"}">
            Prev
        </button>
    `;

  // Page numbers
  const maxVisible = 5;
  let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
  let endPage = Math.min(totalPages, startPage + maxVisible - 1);

  if (endPage - startPage < maxVisible - 1) {
    startPage = Math.max(1, endPage - maxVisible + 1);
  }

  if (startPage > 1) {
    html += `<button onclick="goToPage(1)" class="px-3 py-2 rounded bg-gray-200 hover:bg-gray-300">1</button>`;
    if (startPage > 2) html += `<span class="px-2">...</span>`;
  }

  for (let i = startPage; i <= endPage; i++) {
    html += `
            <button onclick="goToPage(${i})"
                    class="px-3 py-2 rounded ${i === currentPage ? "bg-blue-600 text-white" : "bg-gray-200 hover:bg-gray-300"}">
                ${i}
            </button>
        `;
  }

  if (endPage < totalPages) {
    if (endPage < totalPages - 1) html += `<span class="px-2">...</span>`;
    html += `<button onclick="goToPage(${totalPages})" class="px-3 py-2 rounded bg-gray-200 hover:bg-gray-300">${totalPages}</button>`;
  }

  // Next button
  html += `
        <button onclick="goToPage(${currentPage + 1})"
                ${currentPage === totalPages ? "disabled" : ""}
                class="px-3 py-2 rounded ${currentPage === totalPages ? "bg-gray-200 text-gray-400 cursor-not-allowed" : "bg-blue-600 text-white hover:bg-blue-700"}">
            Next
        </button>
    `;

  html += "</div>";
  container.innerHTML = html;
}

function goToPage(page) {
  if (page < 1 || page > totalPages) return;
  loadListings(page);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function updateStats(total) {
  document.getElementById("stat-total").textContent =
    `${total} resultados encontrados`;
}

function applyFilters() {
  loadListings(1);
}

function clearFilters() {
  document.getElementById("filter-type").value = "";
  document.getElementById("filter-min-price").value = "";
  document.getElementById("filter-max-price").value = "";
  document.getElementById("filter-min-rooms").value = "";
  document.getElementById("filter-max-rooms").value = "";
  document.getElementById("filter-min-bathrooms").value = "";
  document.getElementById("filter-max-bathrooms").value = "";
  document.getElementById("filter-distance").value = 40;
  document.getElementById("distance-value").textContent = "40 km";
  document.getElementById("filter-sort").value = "price-asc";
  loadListings(1);
}

function openModal(index) {
  const listing = allListings[index];
  const images = listing.images || [];
  const typeLabel = listing.property_type === "apartment" ? "Piso" : "Casa";
  const typeColor =
    listing.property_type === "apartment"
      ? "bg-blue-100 text-blue-800"
      : "bg-green-100 text-green-800";

  const rooms = listing.type_attributes?.rooms || listing.rooms;
  const bathrooms = listing.type_attributes?.bathrooms || listing.bathrooms;
  const surface = listing.type_attributes?.surface || listing.square_meters;

  const carouselId = `carousel-${index}`;

  document.getElementById("modal-content").innerHTML = `
        <div class="relative">
            <!-- Carousel -->
            <div class="image-carousel flex overflow-x-auto" id="${carouselId}">
                ${
                  images.length > 0
                    ? images
                        .map(
                          (img, i) => `
                    <img src="${escapeHtml(img)}"
                         alt="Imagen ${i + 1}"
                         class="w-full h-64 md:h-96 object-cover flex-shrink-0"
                         onerror="this.src='https://via.placeholder.com/800x400?text=Error'">
                `,
                        )
                        .join("")
                    : `
                    <div class="w-full h-64 md:h-96 bg-gray-200 flex items-center justify-center text-gray-500">
                        Sin imagenes
                    </div>
                `
                }
            </div>
            ${
              images.length > 1
                ? `
                <button onclick="scrollCarousel('${carouselId}', -1)"
                        class="absolute left-2 top-1/2 -translate-y-1/2 bg-white/90 rounded-full p-2 shadow hover:bg-white text-xl">
                    <-
                </button>
                <button onclick="scrollCarousel('${carouselId}', 1)"
                        class="absolute right-2 top-1/2 -translate-y-1/2 bg-white/90 rounded-full p-2 shadow hover:bg-white text-xl">
                    ->
                </button>
                <div class="absolute bottom-2 left-1/2 -translate-x-1/2 bg-black/60 text-white text-sm px-3 py-1 rounded-full">
                    ${images.length} fotos
                </div>
            `
                : ""
            }
            <button onclick="closeModal()"
                    class="absolute top-2 right-2 bg-white/90 rounded-full w-10 h-10 shadow hover:bg-white text-xl flex items-center justify-center">
                X
            </button>
        </div>

        <div class="p-6">
            <div class="flex flex-wrap items-start justify-between gap-4 mb-4">
                <div>
                    <span class="inline-block ${typeColor} text-sm font-medium px-2 py-1 rounded mb-2">
                        ${typeLabel}
                    </span>
                    <h2 class="text-xl font-bold text-gray-800">${escapeHtml(listing.title)}</h2>
                </div>
                <p class="text-3xl font-bold text-blue-600">
                    ${listing.price}€<span class="text-base font-normal text-gray-500">/mes</span>
                </p>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
                ${
                  rooms
                    ? `
                    <div class="text-center">
                        <p class="text-2xl font-bold">${rooms}</p>
                        <p class="text-sm text-gray-500">Habitaciones</p>
                    </div>
                `
                    : ""
                }
                ${
                  bathrooms
                    ? `
                    <div class="text-center">
                        <p class="text-2xl font-bold">${bathrooms}</p>
                        <p class="text-sm text-gray-500">Banos</p>
                    </div>
                `
                    : ""
                }
                ${
                  surface
                    ? `
                    <div class="text-center">
                        <p class="text-2xl font-bold">${surface}</p>
                        <p class="text-sm text-gray-500">m2</p>
                    </div>
                `
                    : ""
                }
                ${
                  listing.distance_km
                    ? `
                    <div class="text-center">
                        <p class="text-2xl font-bold">${listing.distance_km}</p>
                        <p class="text-sm text-gray-500">km</p>
                    </div>
                `
                    : ""
                }
            </div>

            ${
              listing.description
                ? `
                <div class="mb-6">
                    <h3 class="font-semibold mb-2">Descripcion</h3>
                    <p class="text-gray-600 whitespace-pre-line">${escapeHtml(listing.description)}</p>
                </div>
            `
                : ""
            }

            ${
              listing.location?.city
                ? `
                <div class="mb-6">
                    <h3 class="font-semibold mb-2">Ubicacion</h3>
                    <p class="text-gray-600">
                        ${escapeHtml(listing.location.city)}${listing.location.postal_code ? `, ${listing.location.postal_code}` : ""}
                    </p>
                </div>
            `
                : ""
            }

            <a href="${listing.web_slug ? "https://es.wallapop.com/item/" + listing.web_slug : "#"}"
               target="_blank"
               rel="noopener noreferrer"
               class="block w-full bg-blue-600 text-white text-center rounded-lg px-4 py-3 font-medium hover:bg-blue-700 transition">
                Ver en Wallapop ->
            </a>
        </div>
    `;

  const modal = document.getElementById("modal");
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  document.body.style.overflow = "hidden";
}

function closeModal() {
  const modal = document.getElementById("modal");
  modal.classList.add("hidden");
  modal.classList.remove("flex");
  document.body.style.overflow = "";
}

function scrollCarousel(id, direction) {
  const carousel = document.getElementById(id);
  if (carousel) {
    const scrollAmount = carousel.offsetWidth;
    carousel.scrollBy({ left: scrollAmount * direction, behavior: "smooth" });
  }
}

// Utility: escape HTML to prevent XSS
function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
