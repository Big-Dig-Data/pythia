<i18n src="../locales/common.yaml"></i18n>
<i18n>
en:
  include_works_filter: Include acquired candidates
  unreviewed: Unreviewed
  liked: Liked
  disliked: Disliked
  candidate_updated: Candidate successfuly updated
  score_weights: Score factors
  cancel: Cancel
  apply: Apply
  since: Since
  all: All
  loans_time_filter: Loans time filter
  subjects: Subjects
  authors: Authors
  publisher: Publisher
  languages: Languages
  switch_to_sliders: Switch to slider inputs
  switch_to_numbers: Switch to number inputs
  formats: Formats
  format: Format
  printed: Printed
  unspecified: Unspecified
  other: Other
cs:
  include_works_filter: Zahrnout již zakoupené
  unreviewed: Nehodnocený
  liked: Oblíbený
  disliked: Zamítnutý
  candidate_updated: Kadidát byl úspěšně aktualizován
  score_weights: Paramtery skóre
  cancel: Zrušit
  apply: Aplikovat
  since: Od
  all: Všechno
  loans_time_filter: Časový filtr započítaných výpůjček
  subjects: Témata
  authors: Autoři
  publisher: Vydavatelé
  languages: Jazyk
  switch_to_sliders: Přepnout na posuvníkové zobrazení
  switch_to_numbers: Přepnout na číselné zobrazení
  formats: Formáty
  format: Formát
  printed: Tištěné
  unspecified: Nespecifikováno
  other: Jiné
</i18n>

<template>
  <v-card>
    <v-card-title>
      {{ $t("pages.candidates") }}
      <v-spacer></v-spacer>

      <v-select
        v-model="formatVals"
        :items="formatItems"
        item-value="id"
        item-text="text"
        :label="$t('formats')"
        multiple
        dense
        hide-details
        class="format-select pr-3"
      ></v-select>

      <v-text-field
        v-model="searchDebounced"
        append-icon="fa fa-search"
        :label="$t('search')"
        clearable
        dense
        single-line
        hide-details
        class="format-select"
      ></v-text-field>
    </v-card-title>

    <v-data-table
      :headers="headers"
      :items="rows"
      :options.sync="options"
      :server-items-length="totalRows"
      :loading="loading"
      :single-expand="singleExpand"
      :expanded.sync="expanded"
      :footer-props="{
        'items-per-page-text': $t('table.rows_per_page'),
        'items-per-page-options': $numRowsOpts,
      }"
      item-key="pk"
      show-expand
      dense
    >
      <template v-slot:top>
        <div class="d-flex justify-space-between">
          <v-switch
            v-model="worksFilter"
            @change="fetchData()"
            :label="$t('include_works_filter')"
            class="pa-3 ma-0"
          ></v-switch>

          <v-dialog v-if="showScore" v-model="numberDialog" max-width="800px">
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                color="primary"
                dark
                v-bind="attrs"
                v-on="on"
                class="mt-3 mx-3"
              >
                {{ $t("score_weights") }}
              </v-btn>
            </template>
            <v-card>
              <v-card-title>
                <span class="text-h5">{{ $t("score_weights") }}</span>
              </v-card-title>

              <v-card-text>
                <v-container>
                  <v-row>
                    <v-col col="6">
                      <span>
                        <strong>{{ $t("loans_time_filter") }}:</strong>
                      </span>
                    </v-col>
                    <v-col align="right" class="flex-column">
                      <v-btn-toggle v-model="scoreYearIdx" mandatory>
                        <v-btn small v-for="yr in allScoreYears" :key="yr">
                          {{ `${$t("since")} ${yr}` }}
                        </v-btn>
                        <v-btn small>{{ $t("all") }}</v-btn>
                      </v-btn-toggle>
                    </v-col>
                  </v-row>
                  <v-row class="mt-6">
                    <v-col cols="6" v-for="topic in weightsNames" :key="topic">
                      <v-text-field
                        outlined
                        dense
                        type="number"
                        :label="$t(topic)"
                        :messages="[
                          `${formatInteger(weightsRatio[topic] * 100)}%`,
                        ]"
                        v-model="scoreWeights[topic]"
                      >
                        <template v-slot:prepend>
                          <v-btn
                            text
                            color="blue darken-1"
                            class="pb-3"
                            @click="scoreWeights[topic] *= 2"
                          >
                            2 <v-icon small>fas fa-times</v-icon>
                          </v-btn>
                        </template>
                        <template v-slot:append-outer>
                          <v-btn
                            text
                            color="blue darken-1"
                            class="pb-3"
                            @click="scoreWeights[topic] /= 2"
                          >
                            <v-icon small>fas fa-divide</v-icon> 2
                          </v-btn>
                        </template>
                      </v-text-field>
                    </v-col>
                  </v-row>
                </v-container>
              </v-card-text>

              <v-card-actions class="d-flex justify-space-between">
                <v-btn color="blue darken-1" text @click="switchToSliders">
                  {{ $t("switch_to_sliders") }}
                </v-btn>
                <div>
                  <v-btn
                    color="blue darken-1"
                    text
                    @click="numberDialog = false"
                  >
                    {{ $t("cancel") }}
                  </v-btn>
                  <v-btn color="blue darken-1" text @click="applyWeights">
                    {{ $t("apply") }}
                  </v-btn>
                </div>
              </v-card-actions>
            </v-card>
          </v-dialog>

          <v-dialog v-if="showScore" v-model="sliderDialog" max-width="800px">
            <v-card>
              <v-card-title>
                <span class="text-h5">{{ $t("score_weights") }}</span>
              </v-card-title>

              <v-card-text>
                <v-container>
                  <v-row>
                    <v-col col="6">
                      <span>
                        <strong>{{ $t("loans_time_filter") }}:</strong>
                      </span>
                    </v-col>
                    <v-col align="right" class="flex-column">
                      <v-btn-toggle v-model="scoreYearIdx" mandatory>
                        <v-btn small v-for="yr in allScoreYears" :key="yr">
                          {{ `${$t("since")} ${yr}` }}
                        </v-btn>
                        <v-btn small>{{ $t("all") }}</v-btn>
                      </v-btn-toggle>
                    </v-col>
                  </v-row>
                  <v-row class="mt-6">
                    <v-col cols="6" v-for="topic in weightsNames" :key="topic">
                      <v-slider
                        v-model="scoreWeights[topic]"
                        :label="$t(topic)"
                        thumb-label="always"
                        :thumb-size="24"
                        min="0"
                        max="100"
                      >
                        <template v-slot:append>
                          <span>
                            {{ `${formatInteger(weightsRatio[topic] * 100)}%` }}
                          </span>
                        </template>
                      </v-slider>
                    </v-col>
                  </v-row>
                </v-container>
              </v-card-text>

              <v-card-actions class="d-flex justify-space-between">
                <v-btn color="blue darken-1" text @click="switchToNumbers">
                  {{ $t("switch_to_numbers") }}
                </v-btn>
                <div>
                  <v-btn
                    color="blue darken-1"
                    text
                    @click="sliderDialog = false"
                  >
                    {{ $t("cancel") }}
                  </v-btn>
                  <v-btn color="blue darken-1" text @click="applyWeights">
                    {{ $t("apply") }}
                  </v-btn>
                </div>
              </v-card-actions>
            </v-card>
          </v-dialog>

          <div class="d-flex justify-end mr-4">
            <v-checkbox
              v-model="displayFilters.showUnreviewed"
              :label="$t('unreviewed')"
              color="orange"
              hide-details
              @change="$emit('displayFilters-change', displayFilters)"
            ></v-checkbox>
            <v-checkbox
              class="mx-5"
              v-model="displayFilters.showLiked"
              :label="$t('liked')"
              color="blue lightgreen-2"
              hide-details
              @change="$emit('displayFilters-change', displayFilters)"
            ></v-checkbox>
            <v-checkbox
              v-model="displayFilters.showDisliked"
              :label="$t('disliked')"
              color="red lightgreen-2"
              hide-details
              @change="$emit('displayFilters-change', displayFilters)"
            ></v-checkbox>
          </div>
        </div>
      </template>

      <template v-slot:item.title="{ item }">
        <router-link
          :to="{ name: 'candidate detail', params: { candidateId: item.pk } }"
        >
          {{ item.title }}
        </router-link>
      </template>
      <template v-slot:item.languages="{ item }">
        <span class="item" v-for="lang in item.languages" :key="lang.pk">
          <ExplicitTopicLink topic-type="language" :topic-id="lang.pk">
            {{ lang.name }}
          </ExplicitTopicLink>
          <v-icon x-small class="icon mx-1">fas fa-grip-lines-vertical</v-icon>
        </span>
      </template>
      <template v-slot:item.authors="{ item }">
        <span class="item" v-for="author in item.authors" :key="author.pk">
          <ExplicitTopicLink topic-type="author" :topic-id="author.pk">
            {{ author.name }}
          </ExplicitTopicLink>
          <v-icon x-small class="icon mx-1">fas fa-grip-lines-vertical</v-icon>
        </span>
      </template>
      <template v-slot:item.publisher="{ item }">
        <ExplicitTopicLink topic-type="publisher" :topic-id="item.publisher.pk">
          {{ item.publisher.name }}
        </ExplicitTopicLink>
      </template>
      <template v-slot:item.subjects="{ item }">
        <span class="item" v-for="subject in item.subjects" :key="subject.pk">
          <ExplicitTopicLink topic-type="psh" :topic-id="subject.pk">
            {{ subject.name }}
          </ExplicitTopicLink>
          <v-icon x-small class="icon mx-1">fas fa-grip-lines-vertical</v-icon>
        </span>
      </template>
      <template v-slot:item.score="{ item }">
        {{ formatFloat(item.score) }}
      </template>
      <template v-slot:item.actions="{ item }">
        <span class="d-flex">
          <v-btn
            icon
            color="blue lighten-2"
            @click="toggleLike(item, 'like')"
            :disabled="item.like_diabled"
          >
            <v-icon small>{{ item.like_icon }}</v-icon>
          </v-btn>
          <v-btn
            icon
            color="red lighten-2"
            @click="toggleLike(item, 'dislike')"
            :disabled="item.dislike_diabled"
          >
            <v-icon small>{{ item.dislike_icon }}</v-icon>
          </v-btn>
        </span>
      </template>

      <template v-slot:expanded-item="{ headers, item }">
        <td :colspan="headers.length" class="pa-2">
          <v-simple-table>
            <tbody>
              <tr>
                <th>{{ $t("format") }}</th>
                <td>{{ item.product_format }}</td>
              </tr>
              <tr>
                <th>{{ $t("columns.agent") }}</th>
                <td>{{ item.agent.name }}</td>
              </tr>
              <tr>
                <th>{{ $t("columns.price") }}</th>
                <td>{{ item.price }} {{ item.price_currency }}</td>
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
import { stringify } from "query-string";
import ExplicitTopicLink from "./ExplicitTopicLink";
import { formatInteger, formatFloat, ensureInt } from "../libs/numbers";
import { getCandidateFormat } from "../libs/candidateFormatCodelist";
import isEqual from "lodash/isEqual";
import cloneDeep from "lodash/cloneDeep";

export default {
  name: "CandidatesTable",
  components: { ExplicitTopicLink },

  props: {
    excludeHeaders: { default: () => [], type: Array },
    pageSize: { default: 10, type: Number },
    filters: { default: () => {}, type: Object },
    ordering: {
      default: () => {
        return { sortBy: ["title"], sortDesc: [false] };
      },
      type: Object,
    },
    includeExport: { default: false, type: Boolean },
    scoreYearIdx: { type: Number, default: 5 },
    scoreWeights: {
      type: Object,
      default: () => {
        return { authors: 1, publisher: 1, languages: 1, subjects: 1 };
      },
    },
    displayFilters: {
      type: Object,
      default: () => {
        return { showUnreviewed: true, showLiked: true, showDisliked: false };
      },
    },
    formats: { default: () => [], type: Array },
    yopFrom: { default: null, type: Number },
    yopTo: { default: null, type: Number },
  },

  data() {
    let formatOpts = ["printed", "unspecified", "other"];
    let options = {
      ...this.ordering,
      itemsPerPage: this.$route.query.ps
        ? ensureInt(this.$route.query.ps)
        : this.pageSize,
    };
    if (this.$route.query.page) {
      options["page"] = ensureInt(this.$route.query.page);
    }
    return {
      worksFilter: false,
      expanded: [],
      singleExpand: false,
      dataUrl: "/api/candidates/",
      loading: true,
      search: "",
      options: options,
      // options: { sortBy: ["score"], sortDesc: [true] },
      rows: [],
      totalRows: 0,
      showUnreviewed: true,
      showLiked: true,
      showDisliked: false,
      formatItems: formatOpts.map((el) => ({ id: el, text: this.$i18n.t(el) })),
      formatVals: [...this.formats],
      weightsNames: ["subjects", "authors", "publisher", "languages"],
      allScoreYears: [2020, 2015, 2010, 2005, 2000],
      sliderDialog: false,
      numberDialog: false,
      exportParams: {},
      lastUrlParams: null,
      allHeaders: [
        {
          text: this.$i18n.t("columns.title"),
          value: "title",
          sortable: true,
        },
        {
          text: this.$i18n.t("columns.lang"),
          value: "languages",
          sortable: false,
        },
        {
          text: this.$i18n.t("pages.authors"),
          value: "authors",
          sortable: false,
        },
        {
          text: this.$i18n.t("columns.publisher"),
          value: "publisher",
          sortable: false,
        },
        {
          text: this.$i18n.t("columns.publication_year"),
          value: "publication_year",
          sortable: true,
        },
        {
          text: this.$i18n.t("pages.topics"),
          value: "subjects",
          sortable: false,
        },
        {
          text: this.$i18n.t("columns.score"),
          value: "score",
          sortable: true,
        },
        {
          text: "ISBN",
          value: "isbn",
          sortable: false,
        },
        {
          text: this.$i18n.t("columns.actions"),
          value: "actions",
          sortable: false,
          align: "right",
        },
        { text: "", value: "data-table-expand" },
      ],
    };
  },

  computed: {
    headers() {
      return this.allHeaders.filter(
        (el) => !this.excludeHeaders.includes(el.value)
      );
    },
    showScore() {
      return !this.excludeHeaders.includes("score");
    },
    scoreYear() {
      return [...this.allScoreYears, "all"][this.scoreYearIdx];
    },
    weightsRatio() {
      const total = this.weightsNames.reduce((prev, curr) => {
        return prev + Number(this.scoreWeights[curr]);
      }, 0);
      return this.weightsNames.reduce((prev, curr) => {
        prev[curr] = Number(this.scoreWeights[curr]) / total;
        return prev;
      }, {});
    },
    urlParams() {
      let params = {
        page: this.options.page,
        page_size: this.options.itemsPerPage,
        search: this.search,
        order_by: this.formatSortBy(),
        filters: this.filters,
        works_filter: this.worksFilter ? 0 : 1,
        show_unreviewed: this.displayFilters.showUnreviewed,
        show_liked: this.displayFilters.showLiked,
        show_disliked: this.displayFilters.showDisliked,
        formats: this.formatVals,
        yop_from: this.yopFrom,
        yop_to: this.yopTo,
      };
      if (this.showScore) {
        params["show_score"] = this.showScore;
        params["score_year"] = this.scoreYear;
        params["weights"] = this.weightsRatio;
      }
      return params;
    },
    searchDebounced: {
      get() {
        return this.search;
      },
      set: debounce(function (value) {
        this.search = value;
      }, 500),
    },
    exportUrl() {
      let jsonParams = {};
      Object.entries(this.urlParams).forEach(([k, v]) => {
        jsonParams[k] = typeof v === "object" ? JSON.stringify(v) : v;
      });
      let searchParams = new URLSearchParams(jsonParams);
      return this.dataUrl + "export/?" + searchParams.toString();
    },
  },

  methods: {
    ...mapActions({
      showSnackbar: "showSnackbar",
    }),
    formatInteger,
    formatFloat,
    stringify,
    getCandidateFormat,
    async fetchData() {
      this.loading = true;
      this.lastUrlParams = cloneDeep(this.urlParams);
      try {
        const response = await axios.get(this.dataUrl, {
          params: this.urlParams,
        });
        this.rows = response.data.results.map((el) => {
          for (let like of ["like", "dislike"]) {
            el[`${like}_disabled`] = false;
            el[`${like}_icon`] = this.getLikeIcon(like, el);
          }
          el.product_format = this.getCandidateFormat(el.product_format);
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

    async toggleLike(item, like) {
      const actionVal = item[`${like}d`] ? "remove" : "add";
      item[`${like}_disabled`] = true;
      try {
        const res = await axios.post(`${this.dataUrl}${item.pk}/${like}/`, {
          action_val: actionVal,
        });
        if (res.status === 202) {
          item[`${like}d`] = !item[`${like}d`];
          item[`${like}_icon`] = this.getLikeIcon(like, item);
          this.showSnackbar({
            content: this.$t("candidate_updated"),
            color: "success",
          });
          let case1 = !this.showUnreviewed && !item.liked && !item.disliked;
          let case2 = !this.showLiked && item.liked;
          let case3 = !this.showDisliked && item.disliked;
          if (case1 || case2 || case3) {
            this.rows.splice(this.rows.indexOf(item), 1);
          }
          if (this.rows.length < 10) {
            this.fetchData();
          }
        }
      } catch (error) {
        this.showSnackbar({
          content: "Error updating entry: " + error,
          color: "error",
        });
      } finally {
        item[`${like}_disabled`] = false;
      }
    },

    getLikeIcon(like, item) {
      let thumb = like === "like" ? "up" : "down";
      let iconPrefix = item[`${like}d`] ? "fas" : "far";
      return `${iconPrefix} fa-thumbs-${thumb}`;
    },

    switchToSliders() {
      this.numberDialog = false;
      this.sliderDialog = true;
    },

    switchToNumbers() {
      this.sliderDialog = false;
      this.numberDialog = true;
    },

    applyWeights() {
      this.sliderDialog = false;
      this.numberDialog = false;
      this.fetchData();
      this.$emit("weights-change", {
        weights: this.scoreWeights,
        scoreYearIdx: this.scoreYearIdx,
      });
    },
  },

  watch: {
    urlParams: {
      handler() {
        if (!isEqual(this.urlParams, this.lastUrlParams)) {
          this.fetchData();
        }
      },
      deep: true,
    },
    formatVals() {
      this.$emit("update:formats", [...this.formatVals]);
    },
    formats() {
      if (!isEqual(this.formats, this.formatVals)) {
        this.formatVals = [...this.formats];
      }
    },
    exportUrl: {
      immediate: true,
      handler() {
        this.$emit("export-url-update", this.exportUrl);
      },
    },
    options: {
      deep: true,
      handler() {
        let ordering = {
          sortBy: [...this.options.sortBy],
          sortDesc: [...this.options.sortDesc],
        };
        if (!isEqual(this.ordering, ordering)) {
          this.$emit("update:ordering", ordering);
        }
        history.pushState(
          {},
          null,
          this.$route.path +
            `?page=${this.options.page ?? 1}&ps=${
              this.options.itemsPerPage ?? 1
            }`
        );
      },
    },
    ordering: {
      deep: true,
      handler() {
        Object.assign(this.options, this.ordering);
      },
    },
  },
};
</script>

<style scoped>
.item:last-child .icon {
  display: none;
}
.format-select {
  max-width: 300px;
}
</style>
