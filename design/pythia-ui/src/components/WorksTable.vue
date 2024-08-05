<i18n src="../locales/common.yaml"></i18n>
<i18n>
en:
  acquisition_year: Acquisition year
  acquisition_score: Acquisition score
  missing_date: Missing date
  catalog_year: Catalog year
  full_score: Score
  all: All
cs:
  acquisition_year: Rok akvizice
  acquisition_score: Akviziční skóre
  missing_date: Chybějící datum
  catalog_year: Rok katalogizace
  full_score: Skóre
  all: Všechny
</i18n>
<template>
  <v-card>
    <v-card-title>
      {{ $t("pages.works") }}

      <v-spacer></v-spacer>
      <v-row>
        <v-col v-if="showCatalogYearFilter" cols="6">
          <v-select
            :items="catalogYears"
            :label="$t('catalog_year')"
            :value="selectedYear"
            @change="yearChange"
            solo
            clearable
          ></v-select>
        </v-col>
        <v-col :cols="showCatalogYearFilter ? 6 : 12">
          <v-text-field
            v-model="search"
            append-icon="fa fa-search"
            :label="$t('search')"
            clearable
            single-line
            hide-details
          ></v-text-field>
        </v-col>
      </v-row>
    </v-card-title>

    <v-data-table
      :headers="headers"
      :items="rows"
      :options.sync="options"
      :server-items-length="totalRows"
      :loading="loading"
      :items-per-page="pageSize"
      :single-expand="singleExpand"
      :expanded.sync="expanded"
      :footer-props="{
        'items-per-page-text': $t('table.rows_per_page'),
        'items-per-page-options': $numRowsOpts,
      }"
      item-key="pk"
      show-expand
      dense
      class="elevation-0"
    >
      <template v-slot:item.name="{ item }">
        <router-link :to="{ name: 'work detail', params: { workId: item.pk } }">
          {{ item.name }}
        </router-link>
      </template>
      <template v-slot:item.authors="{ item }">
        <span class="item" v-for="author in item.authors" :key="author.pk">
          <ExplicitTopicLink topic-type="author" :topic-id="author.pk">
            {{ author.name }}
          </ExplicitTopicLink>
          <v-icon x-small class="icon mx-1">fas fa-grip-lines-vertical</v-icon>
        </span>
      </template>
      <template v-slot:item.publishers="{ item }">
        <span
          class="item"
          v-for="publisher in item.publishers"
          :key="publisher.pk"
        >
          <ExplicitTopicLink topic-type="publisher" :topic-id="publisher.pk">
            {{ publisher.name }}
          </ExplicitTopicLink>
          <v-icon x-small class="icon mx-1">fas fa-grip-lines-vertical</v-icon>
        </span>
      </template>
      <template v-slot:item.subject_categories="{ item }">
        <span
          class="item"
          v-for="subject in item.subject_categories"
          :key="subject.pk"
        >
          <ExplicitTopicLink topic-type="psh" :topic-id="subject.pk">
            {{ subject.name }}
          </ExplicitTopicLink>
          <v-icon x-small class="icon mx-1">fas fa-grip-lines-vertical</v-icon>
        </span>
      </template>

      <template v-slot:expanded-item="{ headers, item }">
        <td :colspan="headers.length">
          <v-simple-table>
            <tbody>
              <tr>
                <th>ISBN</th>
                <td>{{ item.isbn.join(", ") }}</td>
              </tr>
              <tr>
                <th>{{ $t("pages.work_types") }}</th>
                <td>
                  <ExplicitTopicLink
                    v-if="item.category"
                    topic-type="work-type"
                    :topic-id="item.category.pk"
                  >
                    {{ item.category.name }}
                  </ExplicitTopicLink>
                </td>
              </tr>
              <tr>
                <th>{{ $t("columns.abstract") }}</th>
                <td>{{ item.abstract }}</td>
              </tr>
            </tbody>
          </v-simple-table>
        </td>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios";
import debounce from "lodash/debounce";
import { mapActions, mapGetters } from "vuex";
import ExplicitTopicLink from "./ExplicitTopicLink";

export default {
  name: "WorksTable",
  components: { ExplicitTopicLink },

  props: {
    excludeHeaders: { default: () => [], type: Array },
    pageSize: { default: 10, type: Number },
    filters: { default: () => {}, type: Object },
    showCatalogYearFilter: { default: false, type: Boolean },
    scoreType: { default: "full_score", type: String },
    catalogYear: { required: false, type: String },
  },

  data() {
    return {
      worksFilter: false,
      expanded: [],
      singleExpand: false,
      loading: false,
      search: "",
      options: {
        sortBy: [
          this.scoreType == "full_score" ? "score" : "acquisition_score",
        ],
        sortDesc: [true],
      },
      rows: [],
      totalRows: 0,
      catalogYears: [],
      selectedYear: this.catalogYear || null,
    };
  },

  computed: {
    ...mapGetters({
      worksetUUID: "selectedWorksetUUID",
      queryParams: "workQueryParams",
    }),
    allHeaders() {
      return [
        {
          text: this.$i18n.t("columns.title"),
          value: "name",
          sortable: false,
        },
        {
          text: this.$i18n.t("columns.lang"),
          value: "lang.name",
          sortable: false,
        },
        {
          text: this.$i18n.t("pages.authors"),
          value: "authors",
          sortable: false,
        },
        {
          text: this.$i18n.t("columns.publisher"),
          value: "publishers",
          sortable: false,
        },
        {
          text: this.$i18n.t("pages.topics"),
          value: "subject_categories",
          sortable: false,
        },
        {
          text: this.$i18n.t(this.scoreType),
          value: this.scoreType == "full_score" ? "score" : "acquisition_score",
          sortable: true,
        },
        {
          text: this.$i18n.t("acquisition_year"),
          value: "acquisition_date",
          sortable: true,
        },
        { text: "", value: "data-table-expand" },
      ];
    },
    headers() {
      return this.allHeaders.filter(
        (el) => !this.excludeHeaders.includes(el.value)
      );
    },
    dataUrl() {
      if (!this.worksetUUID) return null;
      return `api/bookrank/workset/${this.worksetUUID}/works_table/`;
    },
    urlParams() {
      return {
        page: this.options.page,
        page_size: this.options.itemsPerPage,
        search: this.search,
        order_by: this.formatSortBy(),
        filters: this.filters,
        works_filter: this.worksFilter ? 0 : 1,
        catalog_year: this.selectedYear || "",
        score_type: this.scoreType,
        ...this.queryParams,
      };
    },
  },

  methods: {
    ...mapActions({
      showSnackbar: "showSnackbar",
    }),
    async fetchData() {
      if (!this.dataUrl) return null;
      this.loading = true;
      try {
        const response = await axios.get(this.dataUrl, {
          params: this.urlParams,
        });
        this.rows = response.data.results.map((el) => {
          if (el.acquisition_date) {
            el.acquisition_date = el.acquisition_date.slice(0, 4);
          }
          return el;
        });
        this.totalRows = response.data.count;
      } catch (error) {
        this.showSnackbar({
          content: "Error fetching data: " + error,
          color: "error",
        });
      } finally {
        this.loading = false;
      }
    },

    debounceFetchData: debounce(function () {
      this.fetchData();
    }, 500),

    formatSortBy() {
      if (this.options.sortBy.length) {
        let orderBy = this.options.sortBy[0].replace(".", "__");
        let orderSign = this.options.sortDesc[0] ? "-" : "";
        return `${orderSign}${orderBy}`;
      }
      return "";
    },

    async fetchCatalogYears() {
      if (!this.dataUrl || !this.showCatalogYearFilter) return null;
      try {
        const response = await axios.get(`${this.dataUrl}catalog_years/`);
        this.catalogYears = [this.$t("all")].concat(
          ...[
            response.data.map((el) => el[0].slice(0, 4)),
            this.$t("missing_date"),
          ]
        );
      } catch (error) {
        this.showSnackbar({
          content: "Error fetching data: " + error,
          color: "error",
        });
      }
    },

    yearChange(newVal) {
      if (newVal === this.$t("missing_date")) {
        this.selectedYear = "date_missing";
      } else if (newVal === this.$t("all")) {
        this.selectedYear = null;
      } else {
        this.selectedYear = newVal;
      }
    },
  },

  watch: {
    urlParams: {
      handler() {
        this.debounceFetchData();
      },
      deep: true,
    },
    search: {
      handler() {
        if (this.options.page !== 1) {
          this.options.page = 1;
        }
      },
    },
    catalogYear() {
      this.selectedYear = this.catalogYear;
    },
    dataUrl() {
      this.fetchData();
      this.fetchCatalogYears();
    },
  },

  mounted() {
    this.fetchCatalogYears();
  },
};
</script>

<style scoped>
.item:last-child .icon {
  display: none;
}
</style>
