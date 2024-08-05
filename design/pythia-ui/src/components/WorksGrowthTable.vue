<i18n src="../locales/common.yaml"></i18n>
<i18n>
en:
  works_growth_overview: Works growth overview
  absolute_growth: Absolute growth
  relative_growth: Relative growth
  change: Change
cs:
  works_growth_overview: Přehled růstu děl
  absolute_growth: Absolutní růst
  relative_growth: Relativní růst
  change: Změna
</i18n>

<template>
  <v-card>
    <v-card-title>
      {{ $t("works_growth_overview") }}

      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        append-icon="fa fa-search"
        :label="$t('search')"
        clearable
        single-line
        hide-details
      ></v-text-field>
    </v-card-title>

    <v-data-table
      :headers="headers"
      :items="rows"
      :options.sync="options"
      :server-items-length="totalRows"
      :loading="loading"
      :items-per-page="pageSize"
      :footer-props="{
        'items-per-page-text': $t('table.rows_per_page'),
        'items-per-page-options': $numRowsOpts,
      }"
      item-key="pk"
      dense
    >
      <template v-slot:item.name="{ item }">
        <router-link :to="{ name: 'work detail', params: { workId: item.pk } }">
          <ShortenText :text="item.name" :length="40" />
        </router-link>
      </template>
      <template v-slot:item.absolute_growth="{ item }">
        <span :class="`${item.growth_color}--text text--darken-2`">
          {{ item.absolute_growth }}
        </span>
      </template>
      <template v-slot:item.relative_growth="{ item }">
        <span :class="`${item.growth_color}--text text--darken-2`">
          {{ item.relative_growth }}
        </span>
      </template>
      <template v-slot:item.lang="{ item }">
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on">
              <ExplicitTopicLink topic-type="language" :topic-id="item.lang.pk">
                {{ item.lang.name }}
              </ExplicitTopicLink>
              <span
                :class="`${item.lang.growth_color}--text text-caption text--darken-2`"
              >
                {{ item.lang.relative_growth }}
              </span>
            </span>
          </template>
          <span>
            {{ item.lang.relative_growth }} ({{ item.lang.score_yr_b4 }} ->
            {{ item.lang.score_past_yr }})
          </span>
        </v-tooltip>
      </template>
      <template v-slot:item.authors="{ item }">
        <div class="d-flex flex-column">
          <span v-for="author in item.authors" :key="author.pk">
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <span v-bind="attrs" v-on="on">
                  <ExplicitTopicLink topic-type="author" :topic-id="author.pk">
                    {{ author.name }}
                  </ExplicitTopicLink>
                  <span
                    :class="`${author.growth_color}--text text-caption text--darken-2`"
                  >
                    {{ author.relative_growth }}
                  </span>
                </span>
              </template>
              <span>
                {{ author.relative_growth }} ({{ author.score_yr_b4 }} ->
                {{ author.score_past_yr }})
              </span>
            </v-tooltip>
          </span>
        </div>
      </template>
      <template v-slot:item.publishers="{ item }">
        <div class="d-flex flex-column">
          <span v-for="publisher in item.publishers" :key="publisher.pk">
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <span v-bind="attrs" v-on="on">
                  <ExplicitTopicLink
                    topic-type="publisher"
                    :topic-id="publisher.pk"
                  >
                    <ShortenText :text="publisher.name" :length="30" />
                  </ExplicitTopicLink>
                  <span
                    :class="`${publisher.growth_color}--text text-caption text--darken-2`"
                  >
                    {{ publisher.relative_growth }}
                  </span>
                </span>
              </template>
              <span>
                {{ publisher.relative_growth }} ({{ publisher.score_yr_b4 }} ->
                {{ publisher.score_past_yr }})
              </span>
            </v-tooltip>
          </span>
        </div>
      </template>
      <template v-slot:item.subject_categories="{ item }">
        <div class="d-flex flex-column">
          <span v-for="subject in item.subject_categories" :key="subject.pk">
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <span v-bind="attrs" v-on="on">
                  <ExplicitTopicLink topic-type="psh" :topic-id="subject.pk">
                    <ShortenText :text="subject.name" :length="30" />
                  </ExplicitTopicLink>
                  <span
                    :class="`${subject.growth_color}--text text-caption text--darken-2`"
                  >
                    {{ subject.relative_growth }}
                  </span>
                </span>
              </template>
              <span>
                {{ subject.relative_growth }} ({{ subject.score_yr_b4 }} ->
                {{ subject.score_past_yr }})
              </span>
            </v-tooltip>
          </span>
        </div>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios";
import numeral from "numeral";
import debounce from "lodash/debounce";
import { mapActions, mapGetters } from "vuex";
import ExplicitTopicLink from "./ExplicitTopicLink";
import ShortenText from "./ShortenText";

export default {
  name: "WorksGrowthTable",
  components: { ExplicitTopicLink, ShortenText },

  props: {
    pageSize: { default: 10, type: Number },
    filters: { default: () => {}, type: Object },
  },

  data() {
    return {
      loading: false,
      search: "",
      options: { sortBy: ["relative_growth"], sortDesc: [true] },
      rows: [],
      totalRows: 0,
      headers: [
        {
          text: this.$i18n.t("columns.title"),
          value: "name",
          sortable: true,
        },
        {
          text: this.$i18n.t("absolute_growth"),
          value: "absolute_growth",
          sortable: true,
        },
        {
          text: this.$i18n.t("relative_growth"),
          value: "relative_growth",
          sortable: true,
        },
        {
          text: this.$i18n.t("change"),
          value: "change",
          sortable: false,
        },
        {
          text: this.$i18n.t("columns.lang"),
          value: "lang",
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
      ],
    };
  },

  computed: {
    ...mapGetters({
      worksetUUID: "selectedWorksetUUID",
      queryParams: "workQueryParams",
    }),
    dataUrl() {
      if (!this.worksetUUID) return null;
      return `/api/bookrank/workset/${this.worksetUUID}/works_growth_table/`;
    },
    urlParams() {
      return {
        page: this.options.page,
        page_size: this.options.itemsPerPage,
        search: this.search,
        order_by: this.formatSortBy(),
        filters: this.filters,
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
        this.rows = response.data.results.map(this.formatRow);
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

    formatGrowth(val, growthType) {
      if (val == null) return "-";
      let sufix = growthType === "absolute" ? "" : "%";
      return numeral(val).format(`+0,0${sufix}`).replace(/,/g, "\xa0");
    },

    formatETObj(obj) {
      obj.growth_color = obj.absolute_growth > 0 ? "green" : "red";
      obj.relative_growth = this.formatGrowth(obj.relative_growth, "relative");
      return obj;
    },

    formatRow(row) {
      row.growth_color = row.absolute_growth > 0 ? "green" : "red";
      row.absolute_growth = this.formatGrowth(row.absolute_growth, "absolute");
      row.relative_growth = this.formatGrowth(row.relative_growth, "relative");
      row.change = `${row.score_yr_b4}⭢${row.score_past_yr}`;
      row.lang = this.formatETObj(row.lang);
      ["authors", "publishers", "subject_categories"].forEach((et) => {
        row[et] = row[et].map(this.formatETObj);
      });
      return row;
    },
  },

  watch: {
    dataUrl() {
      this.fetchData();
    },
    urlParams: {
      handler() {
        this.fetchData();
      },
      deep: true,
    },
  },
};
</script>
